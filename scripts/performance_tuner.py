#!/usr/bin/env python3
"""
Performance tuning script for face recognition system
"""
import time
import cv2
import numpy as np
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.services.face.recognition_algorithm import FaceRecognitionEngine, load_known_faces_from_directory
from app.utils.performance_config import PerformanceConfig

def benchmark_face_recognition(performance_mode="balanced", test_duration=10):
    """Benchmark face recognition performance"""
    print(f"🔧 Benchmarking face recognition in '{performance_mode}' mode...")
    
    # Load test data
    students_dir = "app/data/images/students"
    if not os.path.exists(students_dir):
        print(f"❌ Students directory not found: {students_dir}")
        return
    
    # Initialize engine
    engine = FaceRecognitionEngine(performance_mode=performance_mode)
    engine.update_known_from_directory(students_dir)
    
    print(f"✅ Loaded {len(engine.known_encodings)} face encodings")
    
    # Create test frame
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Benchmark
    start_time = time.time()
    frame_count = 0
    detection_count = 0
    
    while time.time() - start_time < test_duration:
        # Simulate frame processing
        annotated_frame, detections = engine.recognize_frame(test_frame, draw_annotations=False)
        frame_count += 1
        detection_count += len(detections)
        
        # Add some variation to test frame
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    end_time = time.time()
    total_time = end_time - start_time
    fps = frame_count / total_time
    
    print(f"📊 Results for '{performance_mode}' mode:")
    print(f"   FPS: {fps:.2f}")
    print(f"   Total frames processed: {frame_count}")
    print(f"   Total detections: {detection_count}")
    print(f"   Average detections per frame: {detection_count/frame_count:.2f}")
    print()

def compare_performance_modes():
    """Compare all performance modes"""
    modes = ["fast", "balanced", "accurate"]
    
    print("🚀 Face Recognition Performance Comparison")
    print("=" * 50)
    
    for mode in modes:
        benchmark_face_recognition(mode, test_duration=5)

def optimize_for_your_system():
    """Provide optimization recommendations"""
    print("💡 Optimization Recommendations:")
    print("=" * 40)
    
    # Check system resources
    try:
        import psutil
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        
        print(f"🖥️  System Info:")
        print(f"   CPU cores: {cpu_count}")
        print(f"   Available memory: {memory.available / (1024**3):.1f} GB")
        
        if cpu_count >= 4:
            print("   ✅ Good CPU for face recognition")
        else:
            print("   ⚠️  Consider using 'fast' mode for better performance")
            
        if memory.available > 2 * (1024**3):  # 2GB
            print("   ✅ Sufficient memory available")
        else:
            print("   ⚠️  Low memory - consider 'fast' mode")
            
    except ImportError:
        print("   ℹ️  Install psutil for detailed system analysis")
    
    print("\n🎯 Recommended Settings:")
    print("   For real-time applications: 'fast' mode")
    print("   For accuracy-critical tasks: 'accurate' mode")
    print("   For general use: 'balanced' mode (default)")
    
    print("\n🔧 Manual Tuning:")
    print("   - Increase process_every_n_frames for better performance")
    print("   - Decrease downscale_factor for better accuracy")
    print("   - Adjust min_detection_interval_ms for responsiveness")

def set_performance_mode(mode):
    """Set performance mode"""
    if mode not in ["fast", "balanced", "accurate"]:
        print(f"❌ Invalid mode: {mode}. Use 'fast', 'balanced', or 'accurate'")
        return
    
    PerformanceConfig.set_performance_mode(mode)
    print(f"✅ Performance mode set to: {mode}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "benchmark":
            mode = sys.argv[2] if len(sys.argv) > 2 else "balanced"
            benchmark_face_recognition(mode)
        elif command == "compare":
            compare_performance_modes()
        elif command == "optimize":
            optimize_for_your_system()
        elif command == "set":
            mode = sys.argv[2] if len(sys.argv) > 2 else "balanced"
            set_performance_mode(mode)
        else:
            print("❌ Unknown command. Use: benchmark, compare, optimize, or set")
    else:
        print("🔧 Face Recognition Performance Tuner")
        print("Usage:")
        print("  python performance_tuner.py benchmark [mode]  - Benchmark specific mode")
        print("  python performance_tuner.py compare           - Compare all modes")
        print("  python performance_tuner.py optimize          - Get optimization tips")
        print("  python performance_tuner.py set [mode]        - Set performance mode")
        print("\nModes: fast, balanced, accurate")

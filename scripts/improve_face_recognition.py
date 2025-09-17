#!/usr/bin/env python3
"""
Script to improve face recognition accuracy
"""
import os
import sys
import cv2
import numpy as np
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def main():
    print("🚀 Face Recognition Improvement Script")
    print("=" * 50)
    
    # Check current setup
    check_dependencies()
    
    # Menu
    while True:
        print("\n📋 Choose an option:")
        print("1. Preprocess existing student images")
        print("2. Generate augmented training data")
        print("3. Test recognition accuracy")
        print("4. Optimize performance settings")
        print("5. Check system requirements")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            preprocess_images()
        elif choice == "2":
            generate_augmented_data()
        elif choice == "3":
            test_accuracy()
        elif choice == "4":
            optimize_performance()
        elif choice == "5":
            check_system_requirements()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'cv2', 'numpy', 'face_recognition', 'sklearn', 'PIL'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'numpy':
                import numpy
            elif package == 'face_recognition':
                import face_recognition
            elif package == 'sklearn':
                import sklearn
            elif package == 'PIL':
                from PIL import Image
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install opencv-python numpy face-recognition scikit-learn pillow")
    else:
        print("✅ All dependencies are installed!")

def preprocess_images():
    """Preprocess existing student images"""
    print("\n🔄 Preprocessing student images...")
    
    students_dir = "app/data/images/students"
    if not os.path.exists(students_dir):
        print(f"❌ Students directory not found: {students_dir}")
        return
    
    try:
        from app.services.face.image_preprocessor import batch_preprocess_students
        
        output_dir = "app/data/images/students_processed"
        batch_preprocess_students(students_dir, output_dir)
        print(f"✅ Preprocessed images saved to: {output_dir}")
        
    except ImportError:
        print("❌ Image preprocessor not available. Make sure all dependencies are installed.")
    except Exception as e:
        print(f"❌ Error during preprocessing: {e}")

def generate_augmented_data():
    """Generate augmented training data"""
    print("\n🔄 Generating augmented training data...")
    
    students_dir = "app/data/images/students"
    if not os.path.exists(students_dir):
        print(f"❌ Students directory not found: {students_dir}")
        return
    
    try:
        from app.services.face.image_preprocessor import ImagePreprocessor
        
        preprocessor = ImagePreprocessor()
        output_dir = "app/data/images/students_augmented"
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        total_processed = 0
        for student_folder in os.listdir(students_dir):
            student_path = os.path.join(students_dir, student_folder)
            if not os.path.isdir(student_path):
                continue
            
            print(f"   Processing {student_folder}...")
            
            # Create output directory
            student_output_dir = os.path.join(output_dir, student_folder)
            os.makedirs(student_output_dir, exist_ok=True)
            
            processed_count = 0
            for file_name in os.listdir(student_path):
                if not file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue
                
                image_path = os.path.join(student_path, file_name)
                saved_paths = preprocessor.preprocess_for_training(image_path, student_output_dir, student_folder)
                processed_count += len(saved_paths)
            
            total_processed += processed_count
            print(f"   ✅ Generated {processed_count} augmented images")
        
        print(f"✅ Total augmented images generated: {total_processed}")
        print(f"📁 Saved to: {output_dir}")
        
    except ImportError:
        print("❌ Image preprocessor not available. Make sure all dependencies are installed.")
    except Exception as e:
        print(f"❌ Error during augmentation: {e}")

def test_accuracy():
    """Test recognition accuracy"""
    print("\n🧪 Testing recognition accuracy...")
    
    try:
        from app.services.face.recognition_algorithm import FaceRecognitionEngine
        
        # Initialize engine
        engine = FaceRecognitionEngine(use_advanced_features=True)
        
        # Load known faces
        students_dir = "app/data/images/students"
        if os.path.exists(students_dir):
            engine.update_known_from_directory(students_dir)
            print(f"✅ Loaded {len(engine.known_encodings)} face encodings")
        else:
            print(f"❌ Students directory not found: {students_dir}")
            return
        
        # Test with camera
        print("📷 Starting camera test...")
        print("Press 'q' to quit, 's' to save test image")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Could not open camera")
            return
        
        frame_count = 0
        correct_detections = 0
        total_detections = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            annotated_frame, detections = engine.recognize_frame(frame, draw_annotations=True)
            
            # Count detections
            for detection in detections:
                if detection['is_known']:
                    correct_detections += 1
                total_detections += 1
            
            # Display frame
            cv2.imshow('Face Recognition Test', annotated_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite(f'test_frame_{frame_count}.jpg', annotated_frame)
                print(f"💾 Saved test frame: test_frame_{frame_count}.jpg")
            
            frame_count += 1
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Calculate accuracy
        if total_detections > 0:
            accuracy = (correct_detections / total_detections) * 100
            print(f"📊 Recognition Accuracy: {accuracy:.1f}%")
            print(f"   Correct detections: {correct_detections}")
            print(f"   Total detections: {total_detections}")
        else:
            print("⚠️ No detections made during test")
        
    except ImportError:
        print("❌ Recognition engine not available. Make sure all dependencies are installed.")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

def optimize_performance():
    """Optimize performance settings"""
    print("\n⚡ Optimizing performance settings...")
    
    try:
        from app.services.face.gpu_acceleration import optimize_for_gpu
        from scripts.performance_tuner import compare_performance_modes, optimize_for_your_system
        
        # Check GPU optimization
        optimize_for_gpu()
        
        print("\n" + "="*50)
        
        # Check system optimization
        optimize_for_your_system()
        
        print("\n" + "="*50)
        
        # Compare performance modes
        print("🔄 Running performance comparison...")
        compare_performance_modes()
        
    except ImportError:
        print("❌ Performance modules not available.")
    except Exception as e:
        print(f"❌ Error during optimization: {e}")

def check_system_requirements():
    """Check system requirements"""
    print("\n🖥️ System Requirements Check")
    print("=" * 40)
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version >= (3, 7):
        print("✅ Python version is compatible")
    else:
        print("⚠️ Python 3.7+ recommended")
    
    # Check available memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        available_gb = memory.available / (1024**3)
        
        print(f"Total RAM: {total_gb:.1f} GB")
        print(f"Available RAM: {available_gb:.1f} GB")
        
        if available_gb > 2:
            print("✅ Sufficient memory available")
        else:
            print("⚠️ Low memory - consider closing other applications")
    except ImportError:
        print("ℹ️ Install psutil for detailed memory info: pip install psutil")
    
    # Check CPU
    try:
        cpu_count = psutil.cpu_count()
        print(f"CPU cores: {cpu_count}")
        if cpu_count >= 4:
            print("✅ Good CPU for face recognition")
        else:
            print("⚠️ Consider using 'fast' performance mode")
    except:
        print("ℹ️ CPU info not available")
    
    # Check OpenCV
    try:
        import cv2
        print(f"OpenCV version: {cv2.__version__}")
        
        # Check CUDA support
        if cv2.cuda.getCudaEnabledDeviceCount() > 0:
            print("✅ CUDA GPU support available")
        else:
            print("ℹ️ No CUDA support - CPU processing only")
    except:
        print("❌ OpenCV not properly installed")
    
    # Check face_recognition
    try:
        import face_recognition
        print("✅ face_recognition library available")
    except ImportError:
        print("❌ face_recognition library missing")
        print("   Install with: pip install face-recognition")

if __name__ == "__main__":
    main()

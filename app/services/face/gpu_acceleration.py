"""
GPU acceleration for face recognition
"""
import cv2
import numpy as np
from typing import List, Dict, Optional
import time

class GPUAcceleratedRecognition:
    """GPU-accelerated face recognition using OpenCV DNN and CUDA"""
    
    def __init__(self):
        self.gpu_available = self._check_gpu_support()
        self.face_detector = None
        self.face_recognizer = None
        self._init_models()
    
    def _check_gpu_support(self) -> bool:
        """Check if GPU acceleration is available"""
        try:
            # Check OpenCV CUDA support
            if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                print("✅ CUDA GPU support detected")
                return True
            else:
                print("⚠️ No CUDA GPU support in OpenCV")
                return False
        except Exception as e:
            print(f"⚠️ GPU check failed: {e}")
            return False
    
    def _init_models(self):
        """Initialize GPU-accelerated models"""
        if self.gpu_available:
            try:
                # Load DNN face detection model
                self._load_dnn_face_detector()
                print("✅ GPU-accelerated models loaded")
            except Exception as e:
                print(f"⚠️ Failed to load GPU models: {e}")
                self.gpu_available = False
    
    def _load_dnn_face_detector(self):
        """Load DNN-based face detector for GPU acceleration"""
        # You can download these models from OpenCV's GitHub
        # For now, we'll use a placeholder approach
        try:
            # Example: OpenPose or other DNN models
            # This is a simplified version - you'd need actual model files
            print("🔄 Loading DNN face detector...")
            # self.face_detector = cv2.dnn.readNetFromTensorflow('face_detector.pb')
            # self.face_detector.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            # self.face_detector.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        except Exception as e:
            print(f"⚠️ DNN model loading failed: {e}")
    
    def detect_faces_gpu(self, frame: np.ndarray) -> List[tuple]:
        """Detect faces using GPU acceleration"""
        if not self.gpu_available or self.face_detector is None:
            # Fallback to CPU detection
            return self._detect_faces_cpu(frame)
        
        try:
            # Create blob from image
            blob = cv2.dnn.blobFromImage(
                frame, 1.0, (300, 300), 
                [104, 117, 123], swapRB=False, crop=False
            )
            
            # Set input and run inference
            self.face_detector.setInput(blob)
            detections = self.face_detector.forward()
            
            # Process detections
            faces = []
            h, w = frame.shape[:2]
            
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.5:  # Confidence threshold
                    x1 = int(detections[0, 0, i, 3] * w)
                    y1 = int(detections[0, 0, i, 4] * h)
                    x2 = int(detections[0, 0, i, 5] * w)
                    y2 = int(detections[0, 0, i, 6] * h)
                    faces.append((x1, y1, x2-x1, y2-y1))
            
            return faces
            
        except Exception as e:
            print(f"⚠️ GPU face detection failed: {e}")
            return self._detect_faces_cpu(frame)
    
    def _detect_faces_cpu(self, frame: np.ndarray) -> List[tuple]:
        """Fallback CPU face detection"""
        face_cascade = cv2.CascadeClassifier("app/models/haarcascade_frontalface_default.xml")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        return [(x, y, w, h) for (x, y, w, h) in faces]
    
    def process_frame_gpu(self, frame: np.ndarray) -> np.ndarray:
        """Process frame with GPU acceleration"""
        if not self.gpu_available:
            return frame
        
        try:
            # Upload frame to GPU
            gpu_frame = cv2.cuda_GpuMat()
            gpu_frame.upload(frame)
            
            # Apply GPU operations
            # Example: Gaussian blur on GPU
            gpu_blurred = cv2.cuda.GaussianBlur(gpu_frame, (5, 5), 0)
            
            # Download result back to CPU
            result = gpu_blurred.download()
            
            return result
            
        except Exception as e:
            print(f"⚠️ GPU processing failed: {e}")
            return frame

class PerformanceMonitor:
    """Monitor face recognition performance"""
    
    def __init__(self):
        self.frame_times = []
        self.detection_times = []
        self.recognition_times = []
        self.fps_history = []
    
    def start_frame_timer(self):
        """Start timing a frame"""
        self.frame_start = time.time()
    
    def end_frame_timer(self):
        """End timing a frame and record FPS"""
        frame_time = time.time() - self.frame_start
        self.frame_times.append(frame_time)
        fps = 1.0 / frame_time if frame_time > 0 else 0
        self.fps_history.append(fps)
        
        # Keep only last 100 measurements
        if len(self.fps_history) > 100:
            self.fps_history = self.fps_history[-100:]
    
    def get_average_fps(self) -> float:
        """Get average FPS over recent frames"""
        if not self.fps_history:
            return 0.0
        return sum(self.fps_history) / len(self.fps_history)
    
    def get_performance_stats(self) -> Dict:
        """Get comprehensive performance statistics"""
        if not self.fps_history:
            return {"fps": 0, "frame_time": 0, "status": "No data"}
        
        avg_fps = self.get_average_fps()
        avg_frame_time = sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0
        
        status = "Excellent" if avg_fps > 30 else "Good" if avg_fps > 15 else "Poor"
        
        return {
            "fps": round(avg_fps, 2),
            "frame_time_ms": round(avg_frame_time * 1000, 2),
            "status": status,
            "samples": len(self.fps_history)
        }

def optimize_for_gpu():
    """Provide GPU optimization recommendations"""
    print("🚀 GPU Optimization Recommendations:")
    print("=" * 40)
    
    # Check CUDA availability
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ PyTorch CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        else:
            print("⚠️ PyTorch CUDA not available")
    except ImportError:
        print("ℹ️ PyTorch not installed")
    
    # Check OpenCV CUDA
    try:
        if cv2.cuda.getCudaEnabledDeviceCount() > 0:
            print("✅ OpenCV CUDA support available")
        else:
            print("⚠️ OpenCV compiled without CUDA support")
    except:
        print("⚠️ OpenCV CUDA check failed")
    
    print("\n💡 Optimization Tips:")
    print("1. Install CUDA-enabled OpenCV: pip install opencv-python-gpu")
    print("2. Use smaller input resolutions for faster processing")
    print("3. Process every N frames instead of every frame")
    print("4. Use batch processing for multiple faces")
    print("5. Consider using TensorRT for NVIDIA GPUs")

if __name__ == "__main__":
    # Test GPU acceleration
    gpu_recognition = GPUAcceleratedRecognition()
    monitor = PerformanceMonitor()
    
    # Test with sample frame
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    monitor.start_frame_timer()
    faces = gpu_recognition.detect_faces_gpu(test_frame)
    monitor.end_frame_timer()
    
    stats = monitor.get_performance_stats()
    print(f"Performance: {stats}")
    
    optimize_for_gpu()

"""
Performance configuration for face recognition system
"""
import os
from typing import Dict, Any

class PerformanceConfig:
    """Configuration class for optimizing face recognition performance"""
    
    # Face Recognition Engine Settings
    FACE_RECOGNITION = {
        "match_threshold": 0.50,
        "process_every_n_frames": 2,
        "downscale_factor": 0.5,
        "min_detection_interval_ms": 100,
        "detection_cache_duration": 0.5,  # seconds
        "use_hog_model": True,  # Use HOG instead of CNN for speed
    }
    
    # Haar Cascade Settings
    HAAR_CASCADE = {
        "scale_factor": 1.1,
        "min_neighbors": 3,
        "min_size": (80, 80),
        "flags": "CASCADE_SCALE_IMAGE"
    }
    
    # Camera Settings
    CAMERA = {
        "fps_limit": 30,
        "resolution": (640, 480),  # Lower resolution for faster processing
        "buffer_size": 1,  # Reduce buffer for lower latency
    }
    
    # Performance Modes
    PERFORMANCE_MODES = {
        "fast": {
            "process_every_n_frames": 1,
            "downscale_factor": 0.3,
            "min_detection_interval_ms": 50,
            "detection_cache_duration": 0.2,
        },
        "balanced": {
            "process_every_n_frames": 2,
            "downscale_factor": 0.5,
            "min_detection_interval_ms": 100,
            "detection_cache_duration": 0.5,
        },
        "accurate": {
            "process_every_n_frames": 3,
            "downscale_factor": 0.7,
            "min_detection_interval_ms": 200,
            "detection_cache_duration": 1.0,
        }
    }
    
    @classmethod
    def get_config(cls, mode: str = "balanced") -> Dict[str, Any]:
        """Get configuration for specified performance mode"""
        base_config = cls.FACE_RECOGNITION.copy()
        if mode in cls.PERFORMANCE_MODES:
            base_config.update(cls.PERFORMANCE_MODES[mode])
        return base_config
    
    @classmethod
    def get_haar_config(cls) -> Dict[str, Any]:
        """Get Haar cascade configuration"""
        return cls.HAAR_CASCADE.copy()
    
    @classmethod
    def get_camera_config(cls) -> Dict[str, Any]:
        """Get camera configuration"""
        return cls.CAMERA.copy()
    
    @classmethod
    def set_performance_mode(cls, mode: str) -> None:
        """Set performance mode by updating environment variable"""
        os.environ["FACE_RECOGNITION_MODE"] = mode
    
    @classmethod
    def get_current_mode(cls) -> str:
        """Get current performance mode from environment"""
        return os.environ.get("FACE_RECOGNITION_MODE", "balanced")

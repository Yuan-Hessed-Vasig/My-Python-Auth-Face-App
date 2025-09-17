"""
Advanced confidence scoring and validation for face recognition
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
import cv2
from sklearn.metrics.pairwise import cosine_similarity
import time
from collections import deque

class ConfidenceValidator:
    """Advanced confidence scoring and validation system"""
    
    def __init__(self, 
                 min_confidence: float = 0.6,
                 temporal_window: int = 5,
                 consistency_threshold: float = 0.8):
        self.min_confidence = min_confidence
        self.temporal_window = temporal_window
        self.consistency_threshold = consistency_threshold
        
        # Temporal tracking
        self.detection_history = deque(maxlen=temporal_window)
        self.confidence_history = deque(maxlen=temporal_window)
        
        # Quality metrics
        self.face_quality_weights = {
            'brightness': 0.2,
            'contrast': 0.2,
            'sharpness': 0.3,
            'size': 0.1,
            'angle': 0.2
        }
    
    def calculate_advanced_confidence(self, 
                                    face_encoding: np.ndarray,
                                    known_encodings: List[np.ndarray],
                                    face_region: Tuple[int, int, int, int],
                                    frame: np.ndarray) -> Dict:
        """Calculate advanced confidence score with multiple factors"""
        
        # Basic distance-based confidence
        distances = np.linalg.norm(known_encodings - face_encoding, axis=1)
        min_distance = np.min(distances)
        basic_confidence = max(0, 1 - min_distance)
        
        # Face quality assessment
        quality_score = self._assess_face_quality(face_region, frame)
        
        # Temporal consistency
        temporal_score = self._calculate_temporal_consistency(face_encoding)
        
        # Combined confidence
        advanced_confidence = (
            basic_confidence * 0.5 +
            quality_score * 0.3 +
            temporal_score * 0.2
        )
        
        return {
            'basic_confidence': basic_confidence,
            'quality_score': quality_score,
            'temporal_score': temporal_score,
            'advanced_confidence': advanced_confidence,
            'is_valid': advanced_confidence >= self.min_confidence
        }
    
    def _assess_face_quality(self, face_region: Tuple[int, int, int, int], 
                           frame: np.ndarray) -> float:
        """Assess face quality based on multiple factors"""
        x, y, w, h = face_region
        face_crop = frame[y:y+h, x:x+w]
        
        if face_crop.size == 0:
            return 0.0
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        
        # Brightness assessment
        brightness = np.mean(gray) / 255.0
        brightness_score = 1.0 - abs(brightness - 0.5) * 2  # Optimal around 0.5
        
        # Contrast assessment
        contrast = np.std(gray) / 255.0
        contrast_score = min(1.0, contrast * 4)  # Higher contrast is better
        
        # Sharpness assessment (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(1.0, laplacian_var / 1000.0)  # Normalize
        
        # Size assessment (prefer larger faces)
        face_area = w * h
        size_score = min(1.0, face_area / (100 * 100))  # Normalize to 100x100
        
        # Angle assessment (face orientation)
        angle_score = self._assess_face_angle(face_crop)
        
        # Weighted quality score
        quality_score = (
            brightness_score * self.face_quality_weights['brightness'] +
            contrast_score * self.face_quality_weights['contrast'] +
            sharpness_score * self.face_quality_weights['sharpness'] +
            size_score * self.face_quality_weights['size'] +
            angle_score * self.face_quality_weights['angle']
        )
        
        return quality_score
    
    def _assess_face_angle(self, face_crop: np.ndarray) -> float:
        """Assess face angle (prefer frontal faces)"""
        try:
            # Use face landmarks to determine angle
            # This is a simplified version - you could use dlib's landmark detection
            gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
            
            # Detect eyes
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            eyes = eye_cascade.detectMultiScale(gray, 1.1, 3)
            
            if len(eyes) >= 2:
                # Calculate angle between eyes
                eye_centers = [(x + w//2, y + h//2) for (x, y, w, h) in eyes]
                if len(eye_centers) >= 2:
                    # Simple angle calculation
                    dx = abs(eye_centers[1][0] - eye_centers[0][0])
                    dy = abs(eye_centers[1][1] - eye_centers[0][1])
                    angle = np.arctan2(dy, dx)
                    
                    # Prefer horizontal eye alignment (frontal face)
                    angle_score = 1.0 - abs(angle) / (np.pi / 2)
                    return max(0.0, angle_score)
            
            return 0.5  # Default score if eyes not detected
        except:
            return 0.5
    
    def _calculate_temporal_consistency(self, face_encoding: np.ndarray) -> float:
        """Calculate temporal consistency score"""
        if not self.detection_history:
            return 0.5  # Neutral score for first detection
        
        # Calculate similarity with recent detections
        similarities = []
        for prev_encoding in self.detection_history:
            if prev_encoding is not None:
                similarity = cosine_similarity([face_encoding], [prev_encoding])[0][0]
                similarities.append(similarity)
        
        if not similarities:
            return 0.5
        
        # Return average similarity as consistency score
        return np.mean(similarities)
    
    def update_temporal_history(self, face_encoding: np.ndarray, confidence: float):
        """Update temporal history for consistency tracking"""
        self.detection_history.append(face_encoding)
        self.confidence_history.append(confidence)
    
    def validate_detection(self, detection: Dict) -> Dict:
        """Validate a detection with additional checks"""
        validation_result = {
            'is_valid': True,
            'confidence': detection.get('confidence', 0.0),
            'quality_issues': [],
            'recommendations': []
        }
        
        # Check confidence threshold
        if detection.get('confidence', 0.0) < self.min_confidence:
            validation_result['is_valid'] = False
            validation_result['quality_issues'].append('Low confidence score')
        
        # Check face quality
        quality_score = detection.get('quality_score', 0.0)
        if quality_score < 0.5:
            validation_result['quality_issues'].append('Poor face quality')
            validation_result['recommendations'].append('Improve lighting and camera angle')
        
        # Check temporal consistency
        temporal_score = detection.get('temporal_score', 0.0)
        if temporal_score < 0.3:
            validation_result['quality_issues'].append('Inconsistent detection')
            validation_result['recommendations'].append('Ensure stable face position')
        
        # Check face size
        face_region = detection.get('face_region', (0, 0, 0, 0))
        if len(face_region) == 4:
            x, y, w, h = face_region
            face_area = w * h
            if face_area < 50 * 50:  # Too small
                validation_result['quality_issues'].append('Face too small')
                validation_result['recommendations'].append('Move closer to camera')
            elif face_area > 300 * 300:  # Too large
                validation_result['quality_issues'].append('Face too large')
                validation_result['recommendations'].append('Move away from camera')
        
        return validation_result
    
    def get_confidence_statistics(self) -> Dict:
        """Get confidence statistics over time"""
        if not self.confidence_history:
            return {'average': 0, 'min': 0, 'max': 0, 'samples': 0}
        
        confidences = list(self.confidence_history)
        return {
            'average': np.mean(confidences),
            'min': np.min(confidences),
            'max': np.max(confidences),
            'std': np.std(confidences),
            'samples': len(confidences)
        }
    
    def reset_history(self):
        """Reset temporal history"""
        self.detection_history.clear()
        self.confidence_history.clear()

class MultiFrameValidator:
    """Validate detections across multiple frames"""
    
    def __init__(self, required_frames: int = 3, confidence_threshold: float = 0.7):
        self.required_frames = required_frames
        self.confidence_threshold = confidence_threshold
        self.frame_detections = {}
        self.validated_detections = {}
    
    def add_detection(self, frame_id: int, detection: Dict):
        """Add detection from a frame"""
        student_id = detection.get('student_id')
        if not student_id:
            return
        
        if student_id not in self.frame_detections:
            self.frame_detections[student_id] = []
        
        self.frame_detections[student_id].append({
            'frame_id': frame_id,
            'confidence': detection.get('confidence', 0.0),
            'detection': detection
        })
    
    def validate_student(self, student_id: str) -> bool:
        """Validate if student has enough consistent detections"""
        if student_id not in self.frame_detections:
            return False
        
        detections = self.frame_detections[student_id]
        
        # Check if we have enough frames
        if len(detections) < self.required_frames:
            return False
        
        # Check confidence consistency
        confidences = [d['confidence'] for d in detections]
        avg_confidence = np.mean(confidences)
        
        if avg_confidence < self.confidence_threshold:
            return False
        
        # Check for consistency (low variance)
        confidence_std = np.std(confidences)
        if confidence_std > 0.3:  # High variance indicates inconsistency
            return False
        
        return True
    
    def get_validated_detections(self) -> Dict:
        """Get all validated detections"""
        validated = {}
        for student_id in self.frame_detections:
            if self.validate_student(student_id):
                detections = self.frame_detections[student_id]
                # Get the most recent detection
                latest = max(detections, key=lambda x: x['frame_id'])
                validated[student_id] = latest['detection']
        
        return validated

# Example usage
if __name__ == "__main__":
    # Test confidence validator
    validator = ConfidenceValidator(min_confidence=0.6)
    
    # Simulate detection
    test_encoding = np.random.rand(128)
    test_region = (100, 100, 150, 150)
    test_frame = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
    
    confidence_result = validator.calculate_advanced_confidence(
        test_encoding, [test_encoding], test_region, test_frame
    )
    
    print(f"Confidence result: {confidence_result}")
    
    # Test multi-frame validator
    multi_validator = MultiFrameValidator(required_frames=3)
    
    # Simulate multiple detections
    for i in range(5):
        detection = {
            'student_id': 'test_student',
            'confidence': 0.7 + np.random.normal(0, 0.1),
            'face_region': test_region
        }
        multi_validator.add_detection(i, detection)
    
    is_valid = multi_validator.validate_student('test_student')
    print(f"Multi-frame validation: {is_valid}")

"""
Advanced face recognition using multiple models and techniques
"""
import cv2
import numpy as np
import face_recognition
from typing import List, Dict, Tuple, Optional
import os
import time
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import pickle

class AdvancedFaceRecognition:
    """Advanced face recognition with multiple models and techniques"""
    
    def __init__(self, model_type: str = "ensemble"):
        self.model_type = model_type
        self.known_encodings = []
        self.known_student_ids = []
        self.known_student_info = []
        self.ensemble_models = {}
        self.pca_model = None
        self.confidence_threshold = 0.6
        
        # Initialize different models
        self._init_models()
    
    def _init_models(self):
        """Initialize different recognition models"""
        if self.model_type in ["ensemble", "dlib"]:
            # Dlib-based face_recognition (default)
            self.ensemble_models["dlib"] = {
                "model": "hog",  # or "cnn" for better accuracy
                "tolerance": 0.5
            }
        
        if self.model_type in ["ensemble", "opencv"]:
            # OpenCV LBPH recognizer
            self.ensemble_models["opencv"] = {
                "recognizer": cv2.face.LBPHFaceRecognizer_create(),
                "trained": False
            }
        
        if self.model_type in ["ensemble", "deepface"]:
            # DeepFace model (if available)
            try:
                from deepface import DeepFace
                self.ensemble_models["deepface"] = {
                    "model": DeepFace,
                    "backend": "opencv",  # or "mtcnn", "retinaface"
                    "model_name": "Facenet"  # or "VGG-Face", "ArcFace"
                }
            except ImportError:
                print("⚠️ DeepFace not available. Install with: pip install deepface")
    
    def load_known_faces(self, students_dir: str):
        """Load and process known faces with multiple encodings"""
        print("🔄 Loading known faces with advanced preprocessing...")
        
        # Clear existing data
        self.known_encodings = []
        self.known_student_ids = []
        self.known_student_info = []
        
        # Import preprocessing
        from app.services.face.image_preprocessor import ImagePreprocessor
        preprocessor = ImagePreprocessor()
        
        for student_folder in os.listdir(students_dir):
            student_path = os.path.join(students_dir, student_folder)
            if not os.path.isdir(student_path):
                continue
            
            print(f"   Processing {student_folder}...")
            
            # Get student info
            student_info = self._get_student_info(student_folder)
            
            # Process all images for this student
            for file_name in os.listdir(student_path):
                if not file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue
                
                image_path = os.path.join(student_path, file_name)
                image = cv2.imread(image_path)
                
                if image is None:
                    continue
                
                # Preprocess image
                face_crop = preprocessor.detect_and_crop_face(image)
                if face_crop is None:
                    continue
                
                # Generate multiple encodings
                encodings = self._generate_encodings(face_crop)
                
                if encodings:
                    self.known_encodings.extend(encodings)
                    self.known_student_ids.extend([student_info['id']] * len(encodings))
                    self.known_student_info.extend([student_info] * len(encodings))
        
        # Apply PCA for dimensionality reduction if we have enough samples
        if len(self.known_encodings) > 10:
            self._apply_pca()
        
        print(f"✅ Loaded {len(self.known_encodings)} face encodings for {len(set(self.known_student_ids))} students")
    
    def _get_student_info(self, student_folder: str) -> Dict:
        """Get student information from database or folder name"""
        try:
            from app.services.students_service import StudentsService
            matches = StudentsService.search_students(student_folder)
            if matches:
                for match in matches:
                    if match.get('last_name', '').upper() == student_folder.upper():
                        return match
        except Exception as e:
            print(f"⚠️ Error searching for student {student_folder}: {e}")
        
        # Fallback to folder name
        return {
            'id': student_folder,
            'first_name': student_folder,
            'last_name': student_folder,
            'student_id': student_folder,
            'section': 'Unknown'
        }
    
    def _generate_encodings(self, face_image: np.ndarray) -> List[np.ndarray]:
        """Generate multiple encodings for a single face"""
        encodings = []
        
        # Convert to RGB for face_recognition
        rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        
        # Generate face_recognition encoding
        try:
            face_encodings = face_recognition.face_encodings(rgb_image)
            if face_encodings:
                encodings.extend(face_encodings)
        except Exception as e:
            print(f"⚠️ Error generating face_recognition encoding: {e}")
        
        # Generate additional encodings with different preprocessing
        try:
            # Histogram equalization
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            equalized = cv2.equalizeHist(gray)
            equalized_rgb = cv2.cvtColor(equalized, cv2.COLOR_GRAY2RGB)
            
            face_encodings = face_recognition.face_encodings(equalized_rgb)
            if face_encodings:
                encodings.extend(face_encodings)
        except Exception as e:
            print(f"⚠️ Error generating equalized encoding: {e}")
        
        return encodings
    
    def _apply_pca(self, n_components: int = 128):
        """Apply PCA for dimensionality reduction"""
        try:
            if len(self.known_encodings) > n_components:
                self.pca_model = PCA(n_components=n_components)
                self.known_encodings = self.pca_model.fit_transform(self.known_encodings)
                print(f"✅ Applied PCA: reduced to {n_components} components")
        except Exception as e:
            print(f"⚠️ PCA application failed: {e}")
    
    def recognize_faces(self, frame: np.ndarray) -> List[Dict]:
        """Recognize faces in frame using ensemble methods"""
        if not self.known_encodings:
            return []
        
        # Detect faces
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        
        if not face_locations:
            return []
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        detections = []
        for encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            # Apply PCA if available
            if self.pca_model is not None:
                encoding = self.pca_model.transform([encoding])[0]
            
            # Calculate distances to all known faces
            distances = face_recognition.face_distance(self.known_encodings, encoding)
            
            # Find best match
            best_idx = np.argmin(distances)
            best_distance = distances[best_idx]
            
            # Calculate confidence score
            confidence = max(0, 1 - best_distance)
            
            # Determine if this is a known face
            is_known = confidence >= self.confidence_threshold
            
            student_info = None
            if is_known:
                student_info = self.known_student_info[best_idx]
            
            detections.append({
                'top': top,
                'right': right,
                'bottom': bottom,
                'left': left,
                'student_info': student_info,
                'confidence': confidence,
                'distance': best_distance,
                'is_known': is_known,
                'display_name': self._get_display_name(student_info) if student_info else "UNKNOWN"
            })
        
        return detections
    
    def _get_display_name(self, student_info: Dict) -> str:
        """Get display name from student info"""
        if not student_info:
            return "UNKNOWN"
        
        first_name = student_info.get('first_name', '')
        last_name = student_info.get('last_name', '')
        return f"{first_name} {last_name}".strip()
    
    def train_opencv_model(self, students_dir: str):
        """Train OpenCV LBPH model for ensemble recognition"""
        if "opencv" not in self.ensemble_models:
            return
        
        print("🔄 Training OpenCV LBPH model...")
        
        faces = []
        labels = []
        label_map = {}
        current_label = 0
        
        for student_folder in os.listdir(students_dir):
            student_path = os.path.join(students_dir, student_folder)
            if not os.path.isdir(student_path):
                continue
            
            label_map[student_folder] = current_label
            current_label += 1
            
            for file_name in os.listdir(student_path):
                if not file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue
                
                image_path = os.path.join(student_path, file_name)
                image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                
                if image is None:
                    continue
                
                # Detect and crop face
                face_cascade = cv2.CascadeClassifier("app/models/haarcascade_frontalface_default.xml")
                faces_detected = face_cascade.detectMultiScale(image, 1.1, 5)
                
                for (x, y, w, h) in faces_detected:
                    face_crop = image[y:y+h, x:x+w]
                    face_resized = cv2.resize(face_crop, (100, 100))
                    faces.append(face_resized)
                    labels.append(label_map[student_folder])
        
        if faces:
            self.ensemble_models["opencv"]["recognizer"].train(faces, np.array(labels))
            self.ensemble_models["opencv"]["trained"] = True
            self.ensemble_models["opencv"]["label_map"] = label_map
            print(f"✅ Trained OpenCV model with {len(faces)} face samples")
    
    def save_model(self, model_path: str):
        """Save trained models"""
        model_data = {
            'known_encodings': self.known_encodings,
            'known_student_ids': self.known_student_ids,
            'known_student_info': self.known_student_info,
            'pca_model': self.pca_model,
            'confidence_threshold': self.confidence_threshold
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Model saved to {model_path}")
    
    def load_model(self, model_path: str):
        """Load trained models"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.known_encodings = model_data['known_encodings']
            self.known_student_ids = model_data['known_student_ids']
            self.known_student_info = model_data['known_student_info']
            self.pca_model = model_data.get('pca_model')
            self.confidence_threshold = model_data.get('confidence_threshold', 0.6)
            
            print(f"✅ Model loaded from {model_path}")
        except Exception as e:
            print(f"⚠️ Error loading model: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize advanced recognition
    recognizer = AdvancedFaceRecognition(model_type="ensemble")
    
    # Load known faces
    recognizer.load_known_faces("app/data/images/students")
    
    # Train additional models
    recognizer.train_opencv_model("app/data/images/students")
    
    # Save model
    recognizer.save_model("app/models/advanced_face_model.pkl")

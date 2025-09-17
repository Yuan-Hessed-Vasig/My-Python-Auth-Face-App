"""
Advanced image preprocessing for face recognition
"""
import cv2
import numpy as np
from typing import Tuple, List, Optional
import os
from PIL import Image, ImageEnhance

class ImagePreprocessor:
    """Advanced image preprocessing for better face recognition accuracy"""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier("app/models/haarcascade_frontalface_default.xml")
    
    def detect_and_crop_face(self, image: np.ndarray, target_size: Tuple[int, int] = (224, 224)) -> Optional[np.ndarray]:
        """Detect face and crop to target size with padding"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(100, 100)
        )
        
        if len(faces) == 0:
            return None
            
        # Get the largest face
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = largest_face
        
        # Add padding around face
        padding = 0.2
        pad_w = int(w * padding)
        pad_h = int(h * padding)
        
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(image.shape[1], x + w + pad_w)
        y2 = min(image.shape[0], y + h + pad_h)
        
        face_crop = image[y1:y2, x1:x2]
        
        # Resize to target size
        face_resized = cv2.resize(face_crop, target_size)
        return face_resized
    
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Apply various enhancements to improve image quality"""
        # Convert to PIL for easier manipulation
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(1.2)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(1.1)
        
        # Convert back to OpenCV format
        enhanced = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def normalize_lighting(self, image: np.ndarray) -> np.ndarray:
        """Normalize lighting conditions"""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        
        # Convert back to BGR
        normalized = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        return normalized
    
    def augment_image(self, image: np.ndarray) -> List[np.ndarray]:
        """Generate augmented versions of the image"""
        augmented_images = [image]  # Original image
        
        # Rotation variations
        for angle in [-10, -5, 5, 10]:
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, rotation_matrix, (w, h))
            augmented_images.append(rotated)
        
        # Brightness variations
        for factor in [0.8, 1.2]:
            brightened = cv2.convertScaleAbs(image, alpha=factor, beta=0)
            augmented_images.append(brightened)
        
        # Gaussian blur (slight)
        blurred = cv2.GaussianBlur(image, (3, 3), 0)
        augmented_images.append(blurred)
        
        return augmented_images
    
    def preprocess_for_training(self, image_path: str, output_dir: str, student_id: str) -> List[str]:
        """Preprocess a single image for training"""
        image = cv2.imread(image_path)
        if image is None:
            return []
        
        # Detect and crop face
        face_crop = self.detect_and_crop_face(image)
        if face_crop is None:
            print(f"⚠️ No face detected in {image_path}")
            return []
        
        # Enhance the image
        enhanced = self.enhance_image(face_crop)
        
        # Normalize lighting
        normalized = self.normalize_lighting(enhanced)
        
        # Generate augmented versions
        augmented_images = self.augment_image(normalized)
        
        # Save all versions
        saved_paths = []
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        for i, aug_image in enumerate(augmented_images):
            output_path = os.path.join(output_dir, f"{student_id}_{base_name}_aug_{i}.jpg")
            cv2.imwrite(output_path, aug_image)
            saved_paths.append(output_path)
        
        return saved_paths

def batch_preprocess_students(students_dir: str, output_dir: str):
    """Preprocess all student images"""
    preprocessor = ImagePreprocessor()
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for student_folder in os.listdir(students_dir):
        student_path = os.path.join(students_dir, student_folder)
        if not os.path.isdir(student_path):
            continue
            
        print(f"🔄 Processing {student_folder}...")
        
        # Create output directory for this student
        student_output_dir = os.path.join(output_dir, student_folder)
        os.makedirs(student_output_dir, exist_ok=True)
        
        processed_count = 0
        for file_name in os.listdir(student_path):
            if not file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
                
            image_path = os.path.join(student_path, file_name)
            saved_paths = preprocessor.preprocess_for_training(image_path, student_output_dir, student_folder)
            processed_count += len(saved_paths)
        
        print(f"✅ Processed {processed_count} images for {student_folder}")

if __name__ == "__main__":
    # Example usage
    students_dir = "app/data/images/students"
    output_dir = "app/data/images/students_processed"
    batch_preprocess_students(students_dir, output_dir)



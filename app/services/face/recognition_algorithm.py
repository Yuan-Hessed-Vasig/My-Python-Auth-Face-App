import os
from typing import List, Tuple, Dict, Optional

import cv2
import numpy as np
import face_recognition
import time

# Check for GPU availability
try:
    import dlib
    GPU_AVAILABLE = dlib.DLIB_USE_CUDA
except ImportError:
    GPU_AVAILABLE = False

# Import performance configuration
try:
    from app.utils.performance_config import PerformanceConfig
except ImportError:
    # Fallback if performance config is not available
    class PerformanceConfig:
        @classmethod
        def get_config(cls, mode="balanced"):
            return {
                "match_threshold": 0.50,
                "process_every_n_frames": 2,
                "downscale_factor": 0.5,
                "min_detection_interval_ms": 100,
                "detection_cache_duration": 0.5,
                "use_hog_model": True,
            }


def load_known_faces_from_directory(students_dir: str) -> Tuple[List[np.ndarray], List[str], List[Dict]]:
    """
    Load student images from a directory structure and build face encodings.

    Expected structure:
      students_dir/
        StudentNameA/ image1.jpg, image2.png, ...
        StudentNameB/ ...

    Returns three parallel lists: encodings, student_ids, and student_info.
    Images that fail to load or have no detectable face are skipped.
    """
    known_encodings: List[np.ndarray] = []
    known_student_ids: List[str] = []
    known_student_info: List[Dict] = []

    if not os.path.isdir(students_dir):
        raise FileNotFoundError(f"Student images folder not found: {students_dir}")

    # Import here to avoid circular imports
    try:
        from app.services.students_service import StudentsService
    except ImportError:
        print("⚠️ Could not import StudentsService, using folder names only")
        StudentsService = None

    for student_folder_name in os.listdir(students_dir):
        student_folder = os.path.join(students_dir, student_folder_name)
        if not os.path.isdir(student_folder):
            continue

        # Try to find student in database by folder name
        student_info = None
        if StudentsService:
            try:
                # Search for student by last name (folder name)
                matches = StudentsService.search_students(student_folder_name)
                if matches:
                    # Find exact match by last name
                    for match in matches:
                        if match.get('last_name', '').upper() == student_folder_name.upper():
                            student_info = match
                            break
            except Exception as e:
                print(f"⚠️ Error searching for student {student_folder_name}: {e}")

        # If no database match, create a basic info dict
        if not student_info:
            student_info = {
                'id': None,
                'first_name': student_folder_name,
                'last_name': student_folder_name,
                'student_id': student_folder_name,
                'section': 'Unknown'
            }

        for file_name in os.listdir(student_folder):
            if not file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            img_path = os.path.join(student_folder, file_name)
            image_bgr = cv2.imread(img_path)
            if image_bgr is None:
                continue

            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(image_rgb)
            if encodings:
                known_encodings.append(encodings[0])
                known_student_ids.append(str(student_info.get('id', student_folder_name)))
                known_student_info.append(student_info)

    return known_encodings, known_student_ids, known_student_info


def get_students_base_dir(project_root: str) -> str:
    return os.path.join(project_root, "app", "data", "images", "students")


def ensure_student_dir(base_dir: str, student_id: str) -> str:
    student_dir = os.path.join(base_dir, student_id)
    os.makedirs(student_dir, exist_ok=True)
    return student_dir


def build_next_image_path(base_dir: str, student_id: str) -> str:
    from datetime import datetime
    student_dir = ensure_student_dir(base_dir, student_id)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return os.path.join(student_dir, f"{student_id}_{ts}.jpg")


class FaceRecognitionEngine:
    """
    Lightweight face recognition engine using face_recognition.

    - Maintains known encodings and names
    - Recognizes faces on frames (with optional downscale and frame-skipping)
    - Returns detections and optionally an annotated frame
    """

    def __init__(
        self,
        known_encodings: Optional[List[np.ndarray]] = None,
        known_student_ids: Optional[List[str]] = None,
        known_student_info: Optional[List[Dict]] = None,
        match_threshold: Optional[float] = None,
        process_every_n_frames: Optional[int] = None,
        downscale_factor: Optional[float] = None,
        min_detection_interval_ms: Optional[int] = None,
        performance_mode: str = "balanced"
    ) -> None:
        # Load configuration
        config = PerformanceConfig.get_config(performance_mode)
        
        self.known_encodings = known_encodings or []
        self.known_student_ids = known_student_ids or []
        self.known_student_info = known_student_info or []
        self.match_threshold = match_threshold if match_threshold is not None else config["match_threshold"]
        self.process_every_n_frames = max(1, process_every_n_frames if process_every_n_frames is not None else config["process_every_n_frames"])
        self.downscale_factor = downscale_factor if downscale_factor is not None else config["downscale_factor"]
        self.min_detection_interval_ms = max(0, int(min_detection_interval_ms if min_detection_interval_ms is not None else config["min_detection_interval_ms"]))

        self._frame_count = 0
        self._last_processed_monotonic = 0.0
        
        # Performance optimizations
        self._last_frame_hash = None
        self._last_detections = []
        self._detection_cache_duration = config["detection_cache_duration"]
        self._last_cache_time = 0.0
        self._use_hog_model = config.get("use_hog_model", True)

    def _annotate_frame(self, frame_bgr: np.ndarray, detections: List[Dict], draw_annotations: bool) -> Tuple[np.ndarray, List[Dict]]:
        """Helper method to annotate frame with detections"""
        if not draw_annotations:
            return frame_bgr, detections
            
        annotated = frame_bgr.copy()
        for d in detections:
            color = (0, 200, 0) if d["is_known"] else (128, 128, 128)
            cv2.rectangle(
                annotated,
                (d["left"], d["top"]),
                (d["right"], d["bottom"]),
                color,
                2,
            )
            label = d["display_name"] if d["is_known"] else "UNKNOWN"
            cv2.rectangle(
                annotated,
                (d["left"], d["bottom"] - 35),
                (d["right"], d["bottom"]),
                color,
                cv2.FILLED,
            )
            cv2.putText(
                annotated,
                label,
                (d["left"] + 6, d["bottom"] - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
                lineType=cv2.LINE_AA,
            )
        return annotated, detections

    def update_known_from_directory(self, students_dir: str) -> None:
        encs, student_ids, student_info = load_known_faces_from_directory(students_dir)
        self.known_encodings = encs
        self.known_student_ids = student_ids
        self.known_student_info = student_info

    def recognize_frame(
        self,
        frame_bgr: np.ndarray,
        draw_annotations: bool = True,
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Recognize faces in a BGR frame.

        Returns (annotated_frame_bgr, detections)
        where detections is a list of dicts:
          {
            'top': int, 'right': int, 'bottom': int, 'left': int,
            'name': str,  # upper-cased student name or 'UNKNOWN'
            'distance': float,
            'is_known': bool
          }

        Uses frame-skipping for performance; non-processed frames are passed-through with empty detections.
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return frame_bgr, []

        # Time-based throttle
        if self.min_detection_interval_ms > 0:
            now = time.monotonic() * 1000.0
            if (now - self._last_processed_monotonic) < self.min_detection_interval_ms:
                return frame_bgr, []

        self._frame_count += 1
        should_process = (self._frame_count % self.process_every_n_frames) == 0

        # Check cache first
        now = time.monotonic()
        if (now - self._last_cache_time) < self._detection_cache_duration and self._last_detections:
            return self._annotate_frame(frame_bgr, self._last_detections, draw_annotations)

        if not should_process:
            # Return frame as-is without detections to reduce CPU load
            return frame_bgr, []

        # Downscale for faster processing
        small_bgr = cv2.resize(
            frame_bgr, (0, 0), fx=self.downscale_factor, fy=self.downscale_factor
        )
        rgb_small = cv2.cvtColor(small_bgr, cv2.COLOR_BGR2RGB)

        # Use HOG model for faster detection (vs CNN) based on config
        model = "hog" if self._use_hog_model else "cnn"
        locations = face_recognition.face_locations(rgb_small, model=model)
        encodings = face_recognition.face_encodings(rgb_small, locations)
        self._last_processed_monotonic = time.monotonic() * 1000.0

        detections: List[Dict] = []

        for enc, (top, right, bottom, left) in zip(encodings, locations):
            student_id = None
            student_info = None
            best_distance = 1.0
            is_known = False

            if self.known_encodings:
                distances = face_recognition.face_distance(self.known_encodings, enc)
                best_idx = int(np.argmin(distances))
                best_distance = float(distances[best_idx])

                if best_distance <= self.match_threshold:
                    is_known = True
                    student_id = self.known_student_ids[best_idx]
                    student_info = self.known_student_info[best_idx]

            # Scale back up to original frame coordinates
            scale = int(1.0 / self.downscale_factor)
            top, right, bottom, left = (
                top * scale,
                right * scale,
                bottom * scale,
                left * scale,
            )

            # Create display name
            display_name = "UNKNOWN"
            if student_info:
                first_name = student_info.get('first_name', '')
                last_name = student_info.get('last_name', '')
                display_name = f"{first_name} {last_name}".strip()

            detections.append(
                {
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "left": left,
                    "student_id": student_id,
                    "student_info": student_info,
                    "display_name": display_name,
                    "distance": best_distance,
                    "is_known": is_known,
                }
            )

        # Cache the detections
        self._last_detections = detections
        self._last_cache_time = time.monotonic()

        return self._annotate_frame(frame_bgr, detections, draw_annotations)



import os
from typing import List, Tuple, Dict, Optional

import cv2
import numpy as np
import face_recognition


def load_known_faces_from_directory(students_dir: str) -> Tuple[List[np.ndarray], List[str]]:
    """
    Load student images from a directory structure and build face encodings.

    Expected structure:
      students_dir/
        StudentNameA/ image1.jpg, image2.png, ...
        StudentNameB/ ...

    Returns two parallel lists: encodings and corresponding uppercase names.
    Images that fail to load or have no detectable face are skipped.
    """
    known_encodings: List[np.ndarray] = []
    known_names: List[str] = []

    if not os.path.isdir(students_dir):
        raise FileNotFoundError(f"Student images folder not found: {students_dir}")

    for student in os.listdir(students_dir):
        student_folder = os.path.join(students_dir, student)
        if not os.path.isdir(student_folder):
            continue

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
                known_names.append(student.upper())

    return known_encodings, known_names


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
        known_names: Optional[List[str]] = None,
        match_threshold: float = 0.50,
        process_every_n_frames: int = 3,
        downscale_factor: float = 0.25,
    ) -> None:
        self.known_encodings = known_encodings or []
        self.known_names = known_names or []
        self.match_threshold = match_threshold
        self.process_every_n_frames = max(1, process_every_n_frames)
        self.downscale_factor = downscale_factor

        self._frame_count = 0

    def update_known_from_directory(self, students_dir: str) -> None:
        encs, names = load_known_faces_from_directory(students_dir)
        self.known_encodings = encs
        self.known_names = names

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

        self._frame_count += 1
        should_process = (self._frame_count % self.process_every_n_frames) == 0

        if not should_process:
            # Return frame as-is without detections to reduce CPU load
            return frame_bgr, []

        # Downscale for faster processing
        small_bgr = cv2.resize(
            frame_bgr, (0, 0), fx=self.downscale_factor, fy=self.downscale_factor
        )
        rgb_small = cv2.cvtColor(small_bgr, cv2.COLOR_BGR2RGB)

        locations = face_recognition.face_locations(rgb_small)
        encodings = face_recognition.face_encodings(rgb_small, locations)

        detections: List[Dict] = []

        for enc, (top, right, bottom, left) in zip(encodings, locations):
            name = "UNKNOWN"
            best_distance = 1.0
            is_known = False

            if self.known_encodings:
                distances = face_recognition.face_distance(self.known_encodings, enc)
                best_idx = int(np.argmin(distances))
                best_distance = float(distances[best_idx])

                if best_distance <= self.match_threshold:
                    is_known = True
                    name = self.known_names[best_idx]

            # Scale back up to original frame coordinates
            scale = int(1.0 / self.downscale_factor)
            top, right, bottom, left = (
                top * scale,
                right * scale,
                bottom * scale,
                left * scale,
            )

            detections.append(
                {
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "left": left,
                    "name": name,
                    "distance": best_distance,
                    "is_known": is_known,
                }
            )

        if draw_annotations:
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
                label = d["name"] if d["is_known"] else "UNKNOWN"
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

        return frame_bgr, detections



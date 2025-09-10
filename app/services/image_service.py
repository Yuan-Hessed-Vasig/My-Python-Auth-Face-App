import os
from typing import List, Optional

import cv2

from app.services.face.recognition_algorithm import (
    get_students_base_dir,
    ensure_student_dir,
    build_next_image_path,
)


def _project_root() -> str:
    # Project root = repo root (two levels up from this file)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def get_student_folder(student_id: str) -> str:
    base_dir = get_students_base_dir(_project_root())
    return ensure_student_dir(base_dir, str(student_id))


def list_student_images(student_id: str) -> List[str]:
    """
    Return absolute file paths of all images for the given student_id.
    Accepts .jpg/.jpeg/.png.
    """
    folder = get_student_folder(student_id)
    if not os.path.isdir(folder):
        return []
    files = []
    for name in os.listdir(folder):
        if name.lower().endswith((".jpg", ".jpeg", ".png")):
            files.append(os.path.join(folder, name))
    files.sort()
    return files


def delete_student_image(student_id: str, file_name: str) -> bool:
    """
    Delete a single image file by name from the student's folder.
    Returns True if deleted, False if not found.
    """
    folder = get_student_folder(student_id)
    target = os.path.join(folder, file_name)
    if os.path.isfile(target):
        os.remove(target)
        return True
    return False


def save_student_image_from_bytes(student_id: str, image_bytes: bytes) -> Optional[str]:
    """
    Save an image (bytes) under the student's folder, generating a timestamped name.
    Returns the saved absolute path, or None on failure.
    """
    base_dir = get_students_base_dir(_project_root())
    dest_path = build_next_image_path(base_dir, str(student_id))
    folder = os.path.dirname(dest_path)
    os.makedirs(folder, exist_ok=True)
    try:
        # Decode bytes with OpenCV then write to disk
        import numpy as np

        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return None
        if not cv2.imwrite(dest_path, img):
            return None
        return dest_path
    except Exception:
        return None


def save_student_image_from_mat(student_id: str, image_bgr) -> Optional[str]:
    """
    Save an image (OpenCV BGR matrix) under the student's folder.
    Returns the saved absolute path, or None on failure.
    """
    base_dir = get_students_base_dir(_project_root())
    dest_path = build_next_image_path(base_dir, str(student_id))
    folder = os.path.dirname(dest_path)
    os.makedirs(folder, exist_ok=True)
    try:
        if image_bgr is None:
            return None
        if not cv2.imwrite(dest_path, image_bgr):
            return None
        return dest_path
    except Exception:
        return None



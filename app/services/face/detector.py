import cv2

face_cascade = cv2.CascadeClassifier("app/models/haarcascade_frontalface_default.xml")


def detect_faces(gray_frame):
    # Optimized parameters for faster detection
    faces = face_cascade.detectMultiScale(
        gray_frame, 
        scaleFactor=1.1,  # Smaller steps for better accuracy
        minNeighbors=3,   # Reduced for faster detection
        minSize=(80, 80), # Smaller minimum size for better detection
        flags=cv2.CASCADE_SCALE_IMAGE  # Use optimized scaling
    )
    return faces

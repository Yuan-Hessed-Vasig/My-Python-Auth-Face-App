import cv2

face_cascade = cv2.CascadeClassifier("app/models/haarcascade_frontalface_default.xml")


def detect_faces(gray_frame):
    faces = face_cascade.detectMultiScale(
        gray_frame, scaleFactor=1.2, minNeighbors=5, minSize=(100, 100)
    )
    return faces

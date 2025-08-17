import cv2


def load_recognizer():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("app/services/face/trainer.yml")
    return recognizer


def recognize_face(gray_frame, face, recognizer):
    (x, y, w, h) = face
    face_img = gray_frame[y : y + h, x : x + w]
    id_, confidence = recognizer.predict(face_img)
    return id_, confidence

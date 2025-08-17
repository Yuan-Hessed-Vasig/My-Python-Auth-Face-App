import cv2
import os
import numpy as np


def train_recognizer(data_dir="data/faces"):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, ids = [], []
    for user_folder in os.listdir(data_dir):
        user_id = int(user_folder.split("_")[0])  # folder name "1_username"
        folder_path = os.path.join(data_dir, user_folder)
        for img_file in os.listdir(folder_path):
            img_path = os.path.join(folder_path, img_file)
            gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            faces.append(gray)
            ids.append(user_id)
    recognizer.train(faces, np.array(ids))
    recognizer.save("app/services/face/trainer.yml")
    return True

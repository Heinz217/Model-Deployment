import cv2
import os
import numpy as np
from PIL import Image


# 假定，已经取得用户的名字和人脸信息
# names=["1","3"]
def predict(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    face_detector = cv2.CascadeClassifier('D:/anaconda/lib/site-packages/cv2/data/haarcascade_frontalface_default.xml')
    confidences = []
    pre_ids=[]
    for imagePath in imagePaths:
        i=0
        img=cv2.imread(imagePath)
        # img = Image.open(imagePath)
        img_numpy = np.array(img, 'uint8')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face=face_detector.detectMultiScale(gray,1.2,5,0,(100,100),(300,300))
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read('C:/Users/86130/PycharmProjects/pythonProject15/trainer.yml')
        for x, y, w, h in face:
            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
            print((id,confidence))
            confidences.append(confidence)
            pre_ids.append(id)
        i+=1
    return confidences, pre_ids

def predicting():
    confidences, pre_ids=predict("C:/Users/86130/PycharmProjects/pythonProject18/pri")
    return confidences, pre_ids

import os
import cv2
import numpy as np
from PIL import Image
import csv


# 网站需要返回用户的注册编码
def getImageAndLABELS(path):
    faceSamples=[] # 人脸数组
    ids=[] #
    labels=[]
    s_labels=[]
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)]
    face_detector=cv2.CascadeClassifier('D:/anaconda/lib/site-packages/cv2/data/haarcascade_frontalface_default.xml')
    for imagePath in imagePaths:
        print(imagePath)
        if imagePath.endswith('.jpg'):
            PIL_img = Image.open(imagePath).convert('L')  # L：灰度图像
            img_numpy = np.array(PIL_img, 'uint8')
            faces = face_detector.detectMultiScale(img_numpy)  # 获取人脸特征
            id = int(os.path.split(imagePath)[1].split('.')[0])
            print(id)
            # print(id)
            label = str(os.path.split(imagePath)[1].split('.')[1])
            # print(label)
            labels.append(label)
            # s_label = label.decode('latin1')
            for x, y, w, h in faces:
                ids.append(id)
                faceSamples.append(img_numpy[y:y + h, x:x + w])  # 仅仅将人脸识别框中的数据提取,得到numpy数组
    # print('labels:',labels)
    # print('fs:',faceSamples)
    ih_labels=LabelstoSpecific(labels)
    # print(ih_labels)
    return faceSamples,ids  # ih_labels

def LabelstoSpecific(labels):
    hash_map= {}
    ih_labels=[]
    for label in labels:
        if label in hash_map:
            ih_labels.append(hash_map[label])
        else:
            hash_value=hash(label)
            hash_map[label]=abs(hash_value)
            ih_labels.append(abs(hash_value))
    with open('string_hash_mapping.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['String', 'Hash Value'])
        for label, hash_value in hash_map.items():
            writer.writerow([label, hash_value])
    print(hash_map)
    return ih_labels


def train(path):
    faces, labels = getImageAndLABELS(path)
    # print(labels)
    labels = np.array(labels)
    print(labels)
    print(faces)
    # 识别器
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('C:/Users/86130/PycharmProjects/pythonProject18/trainer.yml')
    recognizer.update(faces,labels)
    recognizer.train(faces, labels)
    recognizer.write('C:/Users/86130/PycharmProjects/pythonProject18/trainer.yml')


#if __name__=='__main__':
    #path='C:/Users/86130/PycharmProjects/pythonProject15/data2'
    #faces,labels=getImageAndLABELS(path)
    # print(labels)
    #labels=np.array(labels)
    #print(labels)
    #print(faces)
    # 识别器
    #recognizer=cv2.face.LBPHFaceRecognizer_create()
    #recognizer.read('C:/Users/86130/PycharmProjects/pythonProject15/trainer.yml')
    #recognizer.update(faces,labels)
    #recognizer.train(faces,labels)
    #recognizer.write('C:/Users/86130/PycharmProjects/pythonProject15/trainer.yml')

def training():
    train('C:/Users/86130/PycharmProjects/pythonProject18/data2')
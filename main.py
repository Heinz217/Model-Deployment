import csv
import os
import socket
import time
from typing import List
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from queue import Queue

from pydantic import BaseModel
from sms import send_message
import predict
import train
import pandas as pd

app = FastAPI()

# CSV 文件路径
CSV_FILE = "user_id_map.csv"
# 字典用于存储用户 ID 和整数映射关系
user_id_map = {}

message_queue = Queue()

short_queue = Queue()

def save_image(user_id: str, image: bytes):
    # 确保保存图片的文件夹存在
    os.makedirs("data0", exist_ok=True)
    # 为用户创建一个唯一的整数 ID
    if user_id not in user_id_map:
        user_id_map[user_id] = len(user_id_map)
    # 保存图片，文件名为用户整数 ID 加上图片编码
    filename = f"{user_id_map[user_id]}.{user_id}.jpg"
    with open(os.path.join("data0", filename), "wb") as f:
        f.write(image)

def save_image_for_pri(user_id:str, image:bytes):
    os.makedirs("pri",exist_ok=True)
    filename=f"{user_id}.jpg"
    with open(os.path.join("pri", filename), "wb") as f:
        f.write(image)

def load_user_id_map():
    # 从 CSV 文件加载用户 ID 映射关系到字典
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                user_id_map[row[0]] = int(row[1])

def save_user_id_map():
    # 将用户 ID 映射关系保存到 CSV 文件
    with open(CSV_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for user_id, integer_id in user_id_map.items():
            writer.writerow([user_id, integer_id+1])

def delete(path):
    for root,dirs,files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(path,name))

def find_row(pri_id):
    # 检查文件是否存在
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} does not exist.")
        return 'Not found'

    with open(CSV_FILE, mode='r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row and len(row) >= 2 and row[1] == str(pri_id):
                return row[0]
        return 'Not found'


def find_name(pri_ids):
    pri_names = []
    for pri_id in pri_ids:
        pri_name = find_row(pri_id)
        pri_names.append(pri_name)
    return pri_names


# user_ids: List[str], files: List[UploadFile] = File(...)
@app.post("/face/training/")
async def upload_images_and_train(user_ids: List[str], files: List[UploadFile] = File(...)):
    user_ids=str(user_ids)
    user_ids=user_ids[2:-2]
    user_ids=user_ids.split(',')
    print(user_ids)
    print(len(files))
    if len(user_ids) != len(files):
        raise HTTPException(status_code=400, detail="Number not the same.")
    for user_id, file in zip(user_ids, files):
        contents = await file.read()
        save_image(user_id, contents)

    # 保存新的用户 ID 映射关系到 CSV 文件
    save_user_id_map()
    train.training()
    # 增加一个删除函数
    # delete("data0")
    return {"message": "Images uploaded successfully.", "user_ids": user_ids}

@app.post("/face/predicting/")
async def upload_image_and_predict(user_ids: List[str], files: List[UploadFile] = File(...)):
    user_ids = str(user_ids)
    user_ids = user_ids[2:-2]
    user_ids = user_ids.split(',')
    if len(user_ids) != len(files):
        raise HTTPException(status_code=400, detail="Number not the same.")
    for user_id, file in zip(user_ids, files):
        contents = await file.read()
        # 加一个写文件函数
        save_image_for_pri(user_id, contents)

    confidences, pre_ids=predict.predicting()
    # 得到估计id后，查找csv表格，得到用户名字符串。用pre_name代替pri_id
    print(pre_ids)
    pre_names = find_name(pre_ids)
    print(user_ids)
    print(pre_names)
    i=0
    for (user_id, pre_name) in zip(user_ids, pre_names):
        print("userid:"+user_id)
        print("prename:"+pre_name)
        confidence=confidences[i]
        i+=1
        if confidence>80:
            result=0
            message_now={
                "user_id":user_id,
                "result":result
            }
            message_queue.put(message_now)
        else:

            if user_id != pre_name:
                result = 2
                message_now = {
                    "user_id": user_id,
                    "result": result
                }
                message_queue.put(message_now)
            else:
                result = 1
                message_now = {
                    "user_id": user_id,
                    "result": result
                }
                message_queue.put(message_now)

    return {"message": "Success."}

@app.get("/face/results/")
async def return_results(request:Request):
    message = message_queue.get()
    # host=request.client.host
    # port=request.client.port
    # user_endpoint = f"http://{host}:{port}/face/test/"
    host = "192.168.177.107",
    port = 17329
    user_endpoint = f"http://{host}:{port}/face/training/"
    headers = {'Connection': 'close'}
    proxies = {"http": None, "https": None}
    # response = requests.post(user_endpoint, json=message, proxies=proxies, headers=headers, timeout=5)
    retry_counter=1
    while retry_counter < 5:
        try:
            response = requests.post(user_endpoint, json=message, headers=headers, timeout=5)
        except socket.error as error:
            print("Connection Failed due to socket - {}")
            print("Attempting {} of 5")
            time.sleep(3)
            retry_counter += 1
    # if message_queue.empty():
        # 清空预测文件夹
        # delete("pri")
    return message
# 在启动应用时加载用户 ID 映射关系
load_user_id_map()

class M2Send(BaseModel):
    phone_num: str
    name: str
    content: str


@app.post("/short_message/")
async def send_short_message(m2sends: List[M2Send]):
    print(m2sends)
    for m2send in m2sends:
        print(m2send)
        # print(m2send)
        phone_nums = m2send.phone_num
        names = m2send.name
        contents = m2send.content
        print(phone_nums)
        content_all = f"尊敬的{names}，你好。{contents}"
        print(int(phone_nums))
        print(content_all)
        send_message(int(phone_nums), content_all)
        # for phone_num, name, content in zip(phone_nums, names, contents):
            # m, name, content))

    return {"message": "Successfully sent!"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="113.54.234.52", port=17328)



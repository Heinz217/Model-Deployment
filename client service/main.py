import uvicorn
from fastapi import FastAPI, BackgroundTasks
import requests
from fastapi import FastAPI, Request
from queue import Queue
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import tools
import json
from starlette.websockets import WebSocketDisconnect
# from talk import chat

app = FastAPI()

message_queue = Queue()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str

def process_message(message: Message):
    # 在后台处理消息
    # text=message.text
    # 仅在测试条件下运行这一个
    # text=tools.message()
    # 实际上是：text=tools.message(text)
    # text=chat(text)
    text="hello"
    message_now={
        "text":text
    }
    message_queue.put(message_now)


def send_message_to_user(message: Message, request:Request):
    # 从队列中获取消息并发送给用户
    processed_message = message_queue.get()

    # 这里必须改，url是为了测试才这样写的
    user_endpoint = f"http://{processed_message['host']}:{processed_message['port']}/ask/"
    # user_endpoint = f"http://{request.client.host}:{request.client.port}/ask/"
    headers = {'Connection': 'close'}
    proxies = {"http": None, "https": None}
    print(type(processed_message))
    processed_message = {"host": "192.168.177.103",
                         "port": "17327",
                         "text": "Hello, World!"
    }
    response = requests.post(user_endpoint, json=processed_message, proxies=proxies)

@app.post("/ask/{id}")
async def send_message(message: Message, background_tasks: BackgroundTasks):
    print(message)
    # 当用户发送消息时，将其添加到后台任务中处理
    background_tasks.add_task(process_message, message)
    return {"chat_system": "Message received."}

@app.get("/answer/{id}")
async def process_queue(background_tasks: BackgroundTasks):
    # 后台任务，处理队列中的消息并发送给用户
    if message_queue.empty():
        return {"text": "no"}
    else:
        message_now = message_queue.get()
        return message_now


if __name__=='__main__':
    uvicorn.run("main:app",host="113.54.229.73",port=17327,debug=True,reload=True)


import uvicorn
from fastapi import FastAPI, BackgroundTasks
import requests
from fastapi import FastAPI, Request
from queue import Queue
from pydantic import BaseModel
import tools
import json
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

message_queue = Queue()

class Message(BaseModel):
    id: str
    text: str

def process_message(message: Message):
    # 在后台处理消息
    text=message.text
    # 仅在测试条件下运行这一个
    text=tools.message()
    # 实际上是：text=tools.message(text)
    message_now={
        "id": message.id,
        "text":text
    }
    message_queue.put(message_now)

@app.post("/ask/")
async def send_message(message: Message, background_tasks: BackgroundTasks):
    print(message)
    # 当用户发送消息时，将其添加到后台任务中处理
    background_tasks.add_task(process_message, message)
    return {"chat_system": "Message received."}

@app.get("/answer/")
async def process_queue():
    if not message_queue.empty():
        message = message_queue.get()
        text = message.text
        return {
        "id": message.id,
        "text": text
    }
    else:
        return {"chat_system": "No message now."}


if __name__=='__main__':
    uvicorn.run("main:app",host="192.168.177.103",port=17327,debug=True,reload=True)

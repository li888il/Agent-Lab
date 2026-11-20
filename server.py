from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent import Agent


app = FastAPI()
agent = Agent() # 初始化你的Agent

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "ok"}
    #健康检查

@app.post("/chat")
def chat(request: ChatRequest):
    # 直接返回流式生成器
    return StreamingResponse(agent.reply(request.message), media_type="text/plain")
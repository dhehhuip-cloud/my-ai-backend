import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경 변수에서 구글 API 키 가져오기
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class ChatRequest(BaseModel):
    prompt: str


@app.get("/")
def read_root():
    return {"status": "AI Server is running!"}


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=request.prompt
        )
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
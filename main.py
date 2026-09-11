import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

app = FastAPI()

# CORS 설정 (모든 도메인에서 접속 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

# Render 환경변수 GEMINI_API_KEY 로드
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.get("/")
def read_root():
    return {"status": "AI Server is running!"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # gemini-3.6-flash 모델 호출
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=request.prompt
        )
        return {"response": response.text}
    except Exception as e:
        return {"response": f"[서버 에러] {str(e)}"}

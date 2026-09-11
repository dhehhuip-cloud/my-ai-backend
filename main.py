import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai.errors import APIError

# .env 파일에서 환경변수 로드
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

# API 키 설정
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.get("/")
def read_root():
    return {"status": "AI Server is running!"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    max_retries = 3
    delay = 2  # 초 단위 대기 시간

    for attempt in range(max_retries):
        try:
            # gemini-3.5-flash-lite 모델 적용
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=request.prompt
            )
            return {"response": response.text}

        except APIError as e:
            # 429 에러(한도 초과) 발생 시 대기 후 자동 재시도
            if e.code == 429 and attempt < max_retries - 1:
                await asyncio.sleep(delay)
                delay *= 2
                continue
            return {"response": f"[서버 에러] {str(e)}"}
            
        except Exception as e:
            return {"response": f"[서버 에러] {str(e)}"}

import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai.errors import APIError

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

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.get("/")
def read_root():
    return {"status": "AI Server is running!"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    max_retries = 3
    delay = 2

    for attempt in range(max_retries):
        try:
            # 3.6 라인업의 고성능 모델인 gemini-3.6-pro 적용
            response = client.models.generate_content(
                model="gemini-3.6-pro",
                contents=request.prompt
            )
            return {"response": response.text}

        except APIError as e:
            if e.code == 429 and attempt < max_retries - 1:
                await asyncio.sleep(delay)
                delay *= 2
                continue
            return {"response": f"[서버 에러] {str(e)}"}
            
        except Exception as e:
            return {"response": f"[서버 에러] {str(e)}"}

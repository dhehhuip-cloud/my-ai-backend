import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

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
    mode: str = "normal"  # normal 또는 concise

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.get("/")
def read_root():
    return {"status": "AI Server is running!"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # 모드가 'concise'일 경우 프롬프트에 지시사항 추가
        prompt_text = request.prompt
        if request.mode == "concise":
            prompt_text = f"[지시: 답변을 최대한 간결하고 요점만 짧게 핵심만 말해줘.]\n\n질문: {request.prompt}"

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt_text
        )
        return {"response": response.text}
    except Exception as e:
        return {"response": f"[서버 에러] {str(e)}"}

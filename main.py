import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

app = FastAPI()

# 1. CORS 설정 (프론트엔드 파일에서 서버로 접속할 수 있도록 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 요청 데이터 규격 정의
class ChatRequest(BaseModel):
    prompt: str

# 3. Gemini API 클라이언트 초기화 (Render 환경변수 GEMINI_API_KEY 사용)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# 4. 서버 작동 확인용 루트 경로
@app.get("/")
def read_root():
    return {"status": "AI Server is running!"}

# 5. 채팅 API 엔드포인트
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=request.prompt
)
        )
        return {"response": response.text}
    except Exception as e:
        # 에러 발생 시 프론트엔드 화면에 구체적인 에러 내용 전달
        return {"response": f"[서버 에러] {str(e)}"}

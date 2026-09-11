import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

app = FastAPI()

# --------------------------------------------------
# CORS
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Request Model
# --------------------------------------------------
class ChatRequest(BaseModel):
    prompt: str
    mode: str = "normal"  # normal 또는 concise


# --------------------------------------------------
# Gemini Client
# --------------------------------------------------
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY 환경변수가 설정되어 있지 않습니다."
    )

client = genai.Client(api_key=api_key)


# --------------------------------------------------
# 서버 자체 요청 제한
# --------------------------------------------------
# 너무 많은 요청이 Gemini API로 동시에 들어가는 것을 방지합니다.
request_semaphore = asyncio.Semaphore(2)


# --------------------------------------------------
# 기본 응답
# --------------------------------------------------
@app.get("/")
def read_root():
    return {
        "status": "AI Server is running!"
    }


# --------------------------------------------------
# Gemini 호출 함수
# --------------------------------------------------
async def generate_ai_response(prompt_text: str):

    # 최대 2번만 시도
    max_attempts = 2

    for attempt in range(max_attempts):

        try:
            # 동시에 최대 2개의 Gemini 요청만 허용
            async with request_semaphore:

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt_text
                )

            return response.text

        except Exception as e:

            error_message = str(e)

            # ------------------------------------------
            # 429 Quota 초과
            # ------------------------------------------
            if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:

                # 마지막 시도였다면 사용자에게 오류 전달
                if attempt == max_attempts - 1:
                    return (
                        "현재 AI 사용량 한도를 초과했습니다.\n"
                        "잠시 후 다시 시도해주세요."
                    )

                # Google이 알려준 대기 시간이 있으면 사용
                wait_seconds = 45

                # 에러 메시지에서 retryDelay의 숫자를 찾음
                import re

                match = re.search(
                    r"retryDelay.*?(\d+)s",
                    error_message
                )

                if match:
                    wait_seconds = int(match.group(1))

                # 너무 오래 기다리지 않도록 최대 60초
                wait_seconds = min(wait_seconds, 60)

                await asyncio.sleep(wait_seconds)

                continue

            # ------------------------------------------
            # 기타 오류
            # ------------------------------------------
            return f"[서버 에러] {error_message}"

    return "[서버 에러] AI 응답을 받을 수 없습니다."


# --------------------------------------------------
# Chat API
# --------------------------------------------------
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):

    try:

        # 빈 질문 방지
        if not request.prompt.strip():
            return {
                "response": "질문을 입력해주세요."
            }

        # ------------------------------------------
        # Concise 모드
        # ------------------------------------------
        prompt_text = request.prompt

        if request.mode == "concise":

            prompt_text = (
                "[지시: 답변을 최대한 간결하고 요점만 짧게 "
                "핵심만 말해줘.]\n\n"
                f"질문: {request.prompt}"
            )

        # ------------------------------------------
        # Gemini 호출
        # ------------------------------------------
        result = await generate_ai_response(prompt_text)

        return {
            "response": result
        }

    except Exception as e:

        return {
            "response": f"[서버 에러] {str(e)}"
        }

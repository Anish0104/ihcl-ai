import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from groq import Groq
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).parent))

from brief import generate_brief  # noqa: E402
from prompts import PROPERTY_SYSTEM_PROMPTS  # noqa: E402
from rag import format_context, retrieve  # noqa: E402


load_dotenv()

app = FastAPI(title="IHCL AI Staff Intelligence Suite")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "ihcl2024")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    property: str = "pierre"
    password: str = ""


class BriefRequest(BaseModel):
    guest_data: dict = Field(default_factory=dict)
    property: str = "pierre"
    password: str = ""


def require_api_key():
    if not GROQ_API_KEY or not client:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not configured. Add it to your .env file.",
        )


def validate_request_password(password: str):
    if password != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")


def validate_property(property_name: str):
    if property_name not in {"pierre", "ama"}:
        raise HTTPException(status_code=400, detail="Invalid property")


def dedupe_sources(retrieved: list[dict]) -> list[str]:
    sources: list[str] = []
    for item in retrieved:
        source = item["source"]
        if source not in sources:
            sources.append(source)
    return sources


@app.get("/")
async def serve_frontend():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse({"error": "Frontend not found"}, status_code=404)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "IHCL AI Staff Intelligence Suite",
        "groq_configured": bool(GROQ_API_KEY),
    }


@app.post("/api/chat")
async def chat(request: ChatRequest):
    validate_request_password(request.password)
    validate_property(request.property)

    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    latest_message = ""
    for message in reversed(request.messages):
        if message.role == "user":
            latest_message = message.content.strip()
            break

    if not latest_message:
        raise HTTPException(status_code=400, detail="No user message provided")

    if latest_message == "__auth_probe__":
        return JSONResponse({"status": "authenticated"})

    require_api_key()

    retrieved = retrieve(latest_message, request.property, n_results=5)
    context = format_context(retrieved)
    sources = dedupe_sources(retrieved)

    system_with_context = f"""{PROPERTY_SYSTEM_PROMPTS[request.property]}

--- RELEVANT KNOWLEDGE BASE CONTENT ---
{context}
--- END KNOWLEDGE BASE CONTENT ---

When answering, reference source documents naturally. If the retrieved content does not contain the answer, say so honestly and note that the production version with live PMS/CRM data would answer this."""

    messages_for_groq = [{"role": "system", "content": system_with_context}]
    for message in request.messages:
        messages_for_groq.append({"role": message.role, "content": message.content})

    def event(payload: dict) -> str:
        return f"data: {json.dumps(payload)}\n\n"

    async def generate():
        yield event({"type": "sources", "sources": sources})
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=1000,
                messages=messages_for_groq,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield event({"type": "text", "content": delta})
            yield event({"type": "done"})
        except Exception as exc:
            yield event({"type": "error", "content": str(exc)})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/brief")
async def create_brief(request: BriefRequest):
    validate_request_password(request.password)
    validate_property(request.property)

    if not request.guest_data:
        raise HTTPException(status_code=400, detail="No guest data provided")

    require_api_key()

    try:
        brief = generate_brief(request.guest_data, request.property)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"brief": brief}

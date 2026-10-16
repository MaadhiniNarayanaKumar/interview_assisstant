from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import chat, intro

settings = get_settings()

app = FastAPI(title="Interview Assistant", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(intro.router)
app.include_router(chat.router)


@app.get("/health")
def health() -> dict:
    current = get_settings()
    return {
        "status": "ok",
        "gemini_configured": bool(current.gemini_api_key),
        "assemblyai_configured": bool(current.assemblyai_api_key),
        "model": current.gemini_model,
    }

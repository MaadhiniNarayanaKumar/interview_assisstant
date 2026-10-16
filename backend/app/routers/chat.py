from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.errors import MissingAPIKey, ModelError
from app.schemas import ChatRequest, ChatResponse
from app.services.gemini import GeminiCoach
from app.services.memory import sessions

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    session_id = sessions.ensure(body.session_id)
    history = sessions.history(session_id)
    coach = GeminiCoach(get_settings())
    try:
        turn = coach.coach(history, body.message)
    except MissingAPIKey as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ModelError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    sessions.append(session_id, "user", body.message)
    sessions.append(session_id, "assistant", turn.reply)
    return ChatResponse(
        session_id=session_id,
        classification=turn.classification,
        message=turn.reply,
    )

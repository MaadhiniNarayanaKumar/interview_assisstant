from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.services.memory import sessions

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "gemini_configured" in body
    assert "assemblyai_configured" in body


def test_chat_rejects_empty_message() -> None:
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_requires_gemini_key(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "")
    get_settings.cache_clear()
    response = client.post("/chat", json={"message": "How do I introduce myself?"})
    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]
    get_settings.cache_clear()


def test_self_intro_rejects_non_audio() -> None:
    response = client.post(
        "/self-intro",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_self_intro_requires_assemblyai_key(monkeypatch) -> None:
    monkeypatch.setenv("ASSEMBLYAI_API_KEY", "")
    get_settings.cache_clear()
    response = client.post(
        "/self-intro",
        files={"file": ("intro.wav", b"RIFFfake", "audio/wav")},
    )
    assert response.status_code == 503
    assert "ASSEMBLYAI_API_KEY" in response.json()["detail"]
    get_settings.cache_clear()


def test_chat_session_keeps_history(monkeypatch) -> None:
    class FakeTurn:
        classification = "not_ready"
        reply = "Lead with your current role."

    monkeypatch.setattr(
        "app.routers.chat.GeminiCoach.coach",
        lambda self, history, message: FakeTurn(),
    )
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    get_settings.cache_clear()

    first = client.post("/chat", json={"message": "Give me one tip"})
    assert first.status_code == 200
    session_id = first.json()["session_id"]

    second = client.post(
        "/chat",
        json={"message": "What should I say next?", "session_id": session_id},
    )
    assert second.status_code == 200
    assert second.json()["session_id"] == session_id
    stored = sessions.history(session_id)
    assert [turn["role"] for turn in stored] == ["user", "assistant", "user", "assistant"]
    get_settings.cache_clear()

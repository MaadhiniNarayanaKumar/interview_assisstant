import asyncio
import logging
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.errors import MissingAPIKey, ModelError, TranscriptionError
from app.schemas import IntroResponse
from app.services.gemini import GeminiCoach
from app.services.transcription import transcribe_file

logger = logging.getLogger(__name__)

router = APIRouter(tags=["intro"])

MAX_AUDIO_BYTES = 25 * 1024 * 1024
AUDIO_SUFFIXES = {".wav", ".mp3", ".flac", ".m4a", ".webm", ".ogg", ".mp4"}


async def _read_limited(upload: UploadFile) -> bytes:
    chunks = []
    total = 0
    while True:
        chunk = await upload.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_AUDIO_BYTES:
            raise HTTPException(status_code=413, detail="Audio file is larger than 25 MB")
        chunks.append(chunk)
    data = b"".join(chunks)
    if not data:
        raise HTTPException(status_code=400, detail="Audio file is empty")
    return data


def _review(data: bytes, suffix: str) -> IntroResponse:
    settings = get_settings()
    coach = GeminiCoach(settings)
    temp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
            handle.write(data)
            temp_path = handle.name
        transcript = transcribe_file(temp_path, settings.assemblyai_api_key)
        feedback = coach.review_intro(transcript)
        return IntroResponse(transcript=transcript, feedback=feedback)
    except MissingAPIKey as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except TranscriptionError as exc:
        message = str(exc)
        status = 422 if message == "No speech was detected in the audio" else 502
        raise HTTPException(status_code=status, detail=message) from exc
    except ModelError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                logger.warning("Could not delete temporary audio %s", temp_path)


@router.post("/self-intro", response_model=IntroResponse)
async def self_intro(file: UploadFile = File(...)) -> IntroResponse:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in AUDIO_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail="Upload a wav, mp3, flac, m4a, webm, ogg, or mp4 file",
        )
    data = await _read_limited(file)
    return await asyncio.to_thread(_review, data, suffix)

import assemblyai as aai

from app.errors import MissingAPIKey, TranscriptionError


def transcribe_file(path: str, api_key: str) -> str:
    if not api_key:
        raise MissingAPIKey("ASSEMBLYAI_API_KEY")

    aai.settings.api_key = api_key
    transcript = aai.Transcriber().transcribe(path)
    if transcript.status == aai.TranscriptStatus.error:
        detail = transcript.error or "AssemblyAI could not transcribe the audio"
        raise TranscriptionError(detail)

    text = (transcript.text or "").strip()
    if not text:
        raise TranscriptionError("No speech was detected in the audio")
    return text

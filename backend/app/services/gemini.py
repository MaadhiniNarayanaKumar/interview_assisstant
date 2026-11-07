import logging
import time
from typing import Dict, List, Optional, Type, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

from app.config import Settings
from app.errors import MissingAPIKey, ModelError
from app.prompts import COACH_SYSTEM, INTRO_SYSTEM, coach_contents, intro_contents
from app.schemas import CoachTurn, IntroFeedback

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

RETRYABLE_MARKERS = (
    "UNAVAILABLE",
    "high demand",
    "try again later",
    "503",
    "429",
    "RESOURCE_EXHAUSTED",
)


class GeminiCoach:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: Optional[genai.Client] = None

    def _client_or_raise(self) -> genai.Client:
        if not self.settings.gemini_api_key:
            raise MissingAPIKey("GEMINI_API_KEY")
        if self._client is None:
            # Preview/current Gemini models require v1beta; v1 returns 404 NOT_FOUND.
            self._client = genai.Client(
                api_key=self.settings.gemini_api_key.strip(),
                http_options=types.HttpOptions(api_version="v1beta"),
            )
        return self._client

    def _parse(self, response, schema: Type[T]) -> T:
        parsed = response.parsed
        try:
            if isinstance(parsed, schema):
                return parsed
            if isinstance(parsed, dict):
                return schema.model_validate(parsed)
            if response.text:
                return schema.model_validate_json(response.text)
        except ValidationError as exc:
            logger.exception("Gemini returned an unexpected payload")
            raise ModelError("Gemini returned an unexpected payload") from exc
        raise ModelError("Gemini returned an empty response")

    def _generate(self, *, system: str, contents: str, schema: Type[T]) -> T:
        last_error = "unknown error"
        for attempt in range(3):
            try:
                response = self._client_or_raise().models.generate_content(
                    model=self.settings.resolved_gemini_model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        response_mime_type="application/json",
                        response_schema=schema,
                    ),
                )
                return self._parse(response, schema)
            except MissingAPIKey:
                raise
            except ModelError:
                raise
            except Exception as exc:
                last_error = str(exc)
                logger.exception("Gemini request failed (attempt %s)", attempt + 1)
                if not any(marker.lower() in last_error.lower() for marker in RETRYABLE_MARKERS):
                    break
                time.sleep(1.5 * (attempt + 1))

        detail = last_error.strip().splitlines()[0][:240]
        raise ModelError(f"Gemini could not complete the request: {detail}")

    def review_intro(self, transcript: str) -> IntroFeedback:
        return self._generate(
            system=INTRO_SYSTEM,
            contents=intro_contents(transcript),
            schema=IntroFeedback,
        )

    def coach(self, history: List[Dict[str, str]], message: str) -> CoachTurn:
        return self._generate(
            system=COACH_SYSTEM,
            contents=coach_contents(history, message),
            schema=CoachTurn,
        )

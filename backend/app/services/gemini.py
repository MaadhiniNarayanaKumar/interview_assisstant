import logging
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


class GeminiCoach:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client: Optional[genai.Client] = None

    def _client_or_raise(self) -> genai.Client:
        if not self.settings.gemini_api_key:
            raise MissingAPIKey("GEMINI_API_KEY")
        if self._client is None:
            self._client = genai.Client(api_key=self.settings.gemini_api_key)
        return self._client

    def _generate(self, *, system: str, contents: str, schema: Type[T]) -> T:
        try:
            response = self._client_or_raise().models.generate_content(
                model=self.settings.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
        except MissingAPIKey:
            raise
        except Exception as exc:
            logger.exception("Gemini request failed")
            raise ModelError("Gemini could not complete the request") from exc

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

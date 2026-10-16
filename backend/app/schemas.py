from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class IntroFeedback(BaseModel):
    content_clarity: str = Field(description="How clearly the introduction was organized and delivered.")
    feedback: str = Field(description="Specific changes the candidate should make, based only on the transcript.")
    user_character: List[str] = Field(description="One-word traits that the transcript actually supports.")
    user_skills: List[str] = Field(description="Skills the candidate mentioned, as short labels.")
    sentiment: str = Field(description="The emotional tone of the introduction.")


class IntroResponse(BaseModel):
    transcript: str
    feedback: IntroFeedback


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: Optional[str] = Field(default=None, max_length=80)


class CoachTurn(BaseModel):
    classification: Literal["ready", "not_ready"] = Field(
        description=(
            'Use "ready" when the candidate wants to practice speaking now. '
            'Use "not_ready" when they want tips, explanations, sample answers, or questions.'
        )
    )
    reply: str = Field(
        description=(
            "Coaching answer when classification is not_ready. "
            "One concrete speaking exercise when classification is ready."
        )
    )


class ChatResponse(BaseModel):
    session_id: str
    classification: Literal["ready", "not_ready"]
    message: str

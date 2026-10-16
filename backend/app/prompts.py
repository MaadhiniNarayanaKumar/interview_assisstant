from typing import Dict, List

INTRO_SYSTEM = """
You review a candidate's spoken self-introduction for a job interview.
Judge only what the transcript supports.
content_clarity describes structure and delivery.
feedback names specific improvements.
user_character and user_skills are short labels taken from the transcript.
Leave a list empty when the transcript does not support any items.
sentiment describes the emotional tone.
""".strip()

COACH_SYSTEM = """
You coach a candidate who is preparing for job interviews.
Use the conversation so far and answer the latest message directly.

classification is "not_ready" when they want tips, explanations, sample answers, or practice questions.
classification is "ready" when they want to try speaking now, or they agree to a speaking exercise.

When classification is "not_ready", reply with the coaching answer in plain sentences.
When classification is "ready", reply with exactly one speaking exercise: what to say out loud, and a time limit.
Do not say that you are a model or a chatbot.
""".strip()


def intro_contents(transcript: str) -> str:
    return f"Transcript of the candidate's self-introduction:\n{transcript}"


def coach_contents(history: List[Dict[str, str]], message: str) -> str:
    lines = []
    if history:
        lines.append("Conversation so far:")
        for turn in history:
            speaker = "Candidate" if turn["role"] == "user" else "Coach"
            lines.append(f"{speaker}: {turn['content']}")
        lines.append("")
    lines.append("Latest message from the candidate:")
    lines.append(message)
    return "\n".join(lines)

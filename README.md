# Interview Assistant

Backend for interview practice. A candidate can upload a spoken self-introduction for feedback, or chat with a coach that switches into a speaking exercise when they are ready to practice out loud.

The model is Gemini (`GEMINI_API_KEY`). Speech-to-text is AssemblyAI (`ASSEMBLYAI_API_KEY`).

## Layout

```
backend/app/        FastAPI app
  routers/          /self-intro and /chat
  services/         Gemini, AssemblyAI, in-memory chat sessions
ui/                 Next.js page for upload, recording, and feedback
content/            Sample audio clips
```

## Setup

Python 3.10 or newer.

```bash
cp .env.example .env
# fill in GEMINI_API_KEY and ASSEMBLYAI_API_KEY

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
cd ui
npm install
npm run dev
```

Open http://localhost:3000. Upload an audio file or record one, then analyze it. The page calls `POST /self-intro` on the API.

## API

`GET /health` reports whether the two keys are set.

`POST /self-intro` accepts a multipart audio file named `file` (`wav`, `mp3`, `flac`, `m4a`, `webm`, `ogg`, `mp4`, up to 25 MB). The response contains the transcript and structured feedback: clarity, improvements, character labels, skills, and sentiment.

`POST /chat` accepts JSON:

```json
{"message": "How should I explain a gap in my resume?", "session_id": "optional"}
```

The response includes `session_id`, `classification` (`not_ready` or `ready`), and `message`. Send the same `session_id` on later turns so the coach keeps the conversation. `ready` means the message is a speaking exercise to do out loud.

Sessions live in process memory and reset when the server restarts.

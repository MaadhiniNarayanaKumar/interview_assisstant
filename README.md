# Interview Assistant

Practice spoken self-introductions and get structured feedback before a real interview.

Upload an audio file or record from the browser. The backend transcribes the speech with **AssemblyAI**, then **Gemini** returns clarity notes, improvement suggestions, skills mentioned, character traits, and sentiment. A chat coach API is also available for interview tips and speaking exercises.

Branch: `v2`

---

## Features

- **Upload or record** a self-introduction in the Next.js UI
- **3-minute maximum** duration (checked on upload, recording, and before analyze)
- **Transcript + structured feedback** from Gemini
- **Chat coach API** that keeps short in-memory session history
- **Health endpoint** that reports whether API keys are configured

---

## Architecture

```
┌─────────────────────┐         ┌──────────────────────────────┐
│  Next.js UI (ui/)   │  POST   │  FastAPI (backend/app/)      │
│  localhost:3000     │────────▶│  localhost:8000              │
│                     │ /self-  │                              │
│  • file upload      │  intro  │  • AssemblyAI transcription  │
│  • mic recording    │         │  • Gemini structured review  │
│  • results panel    │         │  • /chat coaching sessions   │
└─────────────────────┘         └──────────────────────────────┘
```

| Layer | Stack |
| --- | --- |
| Frontend | Next.js 15, React 19 |
| Backend | FastAPI, Uvicorn, Pydantic Settings |
| Speech-to-text | AssemblyAI |
| LLM | Google Gemini (`google-genai`) |

Secrets stay on the backend. The UI only needs the public API base URL.

---

## Repository layout

```
interview_assisstant/
├── .env.example          # Placeholder env vars (never put real keys here)
├── .gitignore
├── README.md
├── backend/
│   ├── requirements.txt
│   ├── tests/
│   │   └── test_api.py
│   └── app/
│       ├── main.py           # FastAPI app, CORS, /health
│       ├── config.py         # Loads .env from repo root
│       ├── schemas.py        # Request/response models
│       ├── prompts.py        # Gemini system prompts
│       ├── routers/
│       │   ├── intro.py      # POST /self-intro
│       │   └── chat.py       # POST /chat
│       └── services/
│           ├── gemini.py         # Structured Gemini calls
│           ├── transcription.py  # AssemblyAI
│           └── memory.py         # In-memory chat sessions
├── ui/
│   ├── package.json
│   └── app/
│       ├── layout.js
│       ├── page.js           # Upload / record / analyze UI
│       └── globals.css
└── content/                  # Sample audio clips for manual testing
```

---

## Prerequisites

- **Python 3.10+** recommended (3.9 works with library end-of-life warnings)
- **Node.js 18+** and npm
- Accounts / keys:
  - [Google AI Studio](https://aistudio.google.com/) → `GEMINI_API_KEY`
  - [AssemblyAI](https://www.assemblyai.com/) → `ASSEMBLYAI_API_KEY`

---

## Environment variables

Copy the example file at the **repo root** (not inside `backend/`):

```bash
cp .env.example .env
```

| Variable | Required | Description |
| --- | --- | --- |
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `ASSEMBLYAI_API_KEY` | Yes | AssemblyAI API key |
| `GEMINI_MODEL` | No | Defaults to `gemini-flash-latest` |
| `CORS_ORIGINS` | No | Comma-separated allowed origins. Default includes `http://localhost:3000` |

For the UI in production, set:

| Variable | Where | Description |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | Vercel / UI env | Backend base URL, e.g. `https://api.yourdomain.com` |

Locally the UI falls back to `http://localhost:8000` when `NEXT_PUBLIC_API_URL` is unset.

**Do not commit `.env`.** Keep real keys only in local env or your host’s secret store. `.env.example` must stay empty of secrets.

---

## Local setup

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Verify:

```bash
curl http://localhost:8000/health
```

Example response:

```json
{
  "status": "ok",
  "gemini_configured": true,
  "assemblyai_configured": true,
  "model": "gemini-flash-latest"
}
```

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend

In a second terminal:

```bash
cd ui
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Using the UI

1. **Upload audio** — choose a `wav`, `mp3`, `flac`, `m4a`, `webm`, `ogg`, or `mp4` file  
   **or**  
   **Record now** — allow microphone access and speak your introduction
2. Preview the clip in the audio player
3. Click **Analyze introduction**
4. Review:
   - Transcript
   - Clarity
   - What to improve
   - Skills
   - Character
   - Sentiment

### Limits

| Rule | Value |
| --- | --- |
| Max duration | **3 minutes** (UI blocks longer uploads; recording auto-stops at 3:00) |
| Max file size (API) | **25 MB** |
| Accepted formats | wav, mp3, flac, m4a, webm, ogg, mp4 |

Sample clips for manual testing live in `content/` (for example `content/harvard.wav`). Prefer short clips under 3 minutes.

---

## API reference

Base URL (local): `http://localhost:8000`

### `GET /health`

Reports process health and whether keys are present (not whether they are valid).

### `POST /self-intro`

Multipart form upload. Field name must be `file`.

```bash
curl -X POST http://localhost:8000/self-intro \
  -F "file=@content/example.wav"
```

**Success response**

```json
{
  "transcript": "...",
  "feedback": {
    "content_clarity": "...",
    "feedback": "...",
    "user_character": ["focused"],
    "user_skills": ["python"],
    "sentiment": "confident"
  }
}
```

**Common errors**

| Status | Meaning |
| --- | --- |
| 400 | Unsupported file type or empty file |
| 413 | File larger than 25 MB |
| 422 | No speech detected |
| 502 | Transcription or Gemini failure |
| 503 | Missing `GEMINI_API_KEY` or `ASSEMBLYAI_API_KEY` |

### `POST /chat`

JSON body for interview coaching. Not yet wired into the UI.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"How should I open a self-introduction?"}'
```

```json
{
  "session_id": "uuid",
  "classification": "not_ready",
  "message": "Lead with your current role and one concrete win..."
}
```

| Field | Meaning |
| --- | --- |
| `classification` | `not_ready` = coaching reply; `ready` = speaking exercise to do out loud |
| `session_id` | Send this back on later turns to keep conversation context |

Sessions are stored **in process memory** and disappear when the server restarts.

---

## Tests

From `backend/` with the virtualenv active:

```bash
pytest tests -q
```

These cover health, validation, missing-key responses, and session history. They do not call Gemini or AssemblyAI.

---

## Deployment overview

The UI and API are deployed separately.

| Piece | Suggested host | Notes |
| --- | --- | --- |
| `ui/` | **Vercel** | Set Root Directory to `ui`. Set `NEXT_PUBLIC_API_URL` to your API URL. |
| `backend/` | Railway / Render / Fly.io | Start with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set the same secrets as local `.env`. |

### Production checklist

1. Deploy the API and confirm `/health` returns both keys configured
2. Set `CORS_ORIGINS` to your live site, e.g. `https://yourdomain.com,https://www.yourdomain.com`
3. Deploy the UI on Vercel with `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`
4. Attach custom domains:
   - Apex / `www` → Vercel
   - `api` subdomain → backend host
5. Rotate any keys that were ever committed or pasted into chat

---

## Security notes

- Never put real keys in `.env.example`, screenshots, or git commits
- Gemini and AssemblyAI keys belong only on the backend host
- `NEXT_PUBLIC_*` values are visible in the browser; only put the API **URL** there, not secrets
- If a key was exposed, revoke and recreate it in the provider dashboard

---

## Troubleshooting

| Problem | What to check |
| --- | --- |
| UI shows it cannot reach the analysis service | Backend running on port 8000? `NEXT_PUBLIC_API_URL` correct? |
| `503` missing API key | `.env` at repo root filled in? Restart uvicorn after editing `.env` |
| CORS error in the browser | Add the UI origin to `CORS_ORIGINS` and restart the API |
| Microphone blocked | Browser permission denied; upload a file instead |
| Audio rejected as too long | Keep introductions to **3 minutes or less** |
| No speech detected | Quiet/empty recording, wrong format, or very noisy clip |

---

## License / status

Personal interview-practice project on branch `v2`. The UI currently covers self-intro analysis; the `/chat` coach is API-only for now.

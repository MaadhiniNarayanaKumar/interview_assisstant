"use client";

import { useEffect, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const MAX_DURATION_SECONDS = 3 * 60;
const TOO_LONG_MESSAGE =
  "This audio is longer than 3 minutes. Please keep your introduction to a maximum of 3 minutes.";

function extensionFor(mimeType) {
  if (mimeType.includes("mp4")) return "mp4";
  if (mimeType.includes("ogg")) return "ogg";
  if (mimeType.includes("wav")) return "wav";
  return "webm";
}

function formatClock(totalSeconds) {
  const seconds = Math.max(0, Math.floor(totalSeconds));
  const mins = String(Math.floor(seconds / 60)).padStart(2, "0");
  const secs = String(seconds % 60).padStart(2, "0");
  return `${mins}:${secs}`;
}

function getAudioDuration(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const audio = document.createElement("audio");
    audio.preload = "metadata";
    audio.onloadedmetadata = () => {
      const duration = audio.duration;
      URL.revokeObjectURL(url);
      if (!Number.isFinite(duration) || duration <= 0) {
        reject(new Error("Could not read the length of this audio file."));
        return;
      }
      resolve(duration);
    };
    audio.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("Could not read this audio file."));
    };
    audio.src = url;
  });
}

function ChipList({ items }) {
  if (!items?.length) {
    return <span className="empty">None noted</span>;
  }
  return (
    <div className="chips">
      {items.map((item) => (
        <span key={item}>{item}</span>
      ))}
    </div>
  );
}

export default function HomePage() {
  const fileInputRef = useRef(null);
  const recorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const recordStartedAtRef = useRef(0);
  const recordTimerRef = useRef(null);
  const maxRecordTimerRef = useRef(null);
  const [audioFile, setAudioFile] = useState(null);
  const [source, setSource] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [recording, setRecording] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  useEffect(() => {
    return () => {
      if (audioUrl) URL.revokeObjectURL(audioUrl);
      streamRef.current?.getTracks().forEach((track) => track.stop());
      if (recordTimerRef.current) clearInterval(recordTimerRef.current);
      if (maxRecordTimerRef.current) clearTimeout(maxRecordTimerRef.current);
    };
  }, [audioUrl]);

  function clearRecordTimers() {
    if (recordTimerRef.current) {
      clearInterval(recordTimerRef.current);
      recordTimerRef.current = null;
    }
    if (maxRecordTimerRef.current) {
      clearTimeout(maxRecordTimerRef.current);
      maxRecordTimerRef.current = null;
    }
  }

  function clearAudioSelection() {
    setAudioFile(null);
    setSource("");
    setAudioUrl((current) => {
      if (current) URL.revokeObjectURL(current);
      return "";
    });
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  async function rememberFile(file, nextSource, knownDuration) {
    setResult(null);
    setError("");

    try {
      const duration =
        typeof knownDuration === "number" ? knownDuration : await getAudioDuration(file);
      if (duration > MAX_DURATION_SECONDS) {
        clearAudioSelection();
        setError(TOO_LONG_MESSAGE);
        return false;
      }
    } catch (err) {
      clearAudioSelection();
      setError(err.message || "Could not read this audio file.");
      return false;
    }

    setSource(nextSource);
    setAudioFile(file);
    setAudioUrl((current) => {
      if (current) URL.revokeObjectURL(current);
      return URL.createObjectURL(file);
    });
    return true;
  }

  async function onFileChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    const accepted = await rememberFile(file, "upload");
    if (!accepted && fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  async function toggleRecording() {
    setError("");
    if (recording) {
      recorderRef.current?.stop();
      return;
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      setError("This browser cannot record audio.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "audio/mp4";
      const recorder = new MediaRecorder(stream, { mimeType });
      chunksRef.current = [];
      recordStartedAtRef.current = Date.now();
      setElapsed(0);

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        clearRecordTimers();
        const durationSeconds = (Date.now() - recordStartedAtRef.current) / 1000;
        stream.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
        setRecording(false);
        setElapsed(0);

        if (durationSeconds > MAX_DURATION_SECONDS) {
          clearAudioSelection();
          setError(TOO_LONG_MESSAGE);
          return;
        }

        const blob = new Blob(chunksRef.current, { type: mimeType });
        const extension = extensionFor(mimeType);
        await rememberFile(
          new File([blob], `introduction.${extension}`, { type: mimeType }),
          "record",
          durationSeconds,
        );
      };

      streamRef.current = stream;
      recorderRef.current = recorder;
      recorder.start();
      setRecording(true);
      setResult(null);

      recordTimerRef.current = setInterval(() => {
        setElapsed(Math.floor((Date.now() - recordStartedAtRef.current) / 1000));
      }, 250);

      maxRecordTimerRef.current = setTimeout(() => {
        if (recorderRef.current?.state === "recording") {
          setError(TOO_LONG_MESSAGE);
          recorderRef.current.stop();
        }
      }, MAX_DURATION_SECONDS * 1000);
    } catch {
      clearRecordTimers();
      setError("Microphone access was blocked. You can still upload a file.");
    }
  }

  async function analyze() {
    if (!audioFile) return;
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const duration = await getAudioDuration(audioFile);
      if (duration > MAX_DURATION_SECONDS) {
        throw new Error(TOO_LONG_MESSAGE);
      }

      const body = new FormData();
      body.append("file", audioFile);
      const response = await fetch(`${API_URL}/self-intro`, {
        method: "POST",
        body,
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = payload.detail;
        const message = typeof detail === "string" ? detail : "The analysis could not be completed.";
        throw new Error(message);
      }
      setResult(payload);
    } catch (err) {
      const unreachable = err.message === "Failed to fetch";
      setError(
        unreachable
          ? "Could not reach the analysis service. Start the API on port 8000 and try again."
          : err.message || "The analysis could not be completed.",
      );
    } finally {
      setBusy(false);
    }
  }

  function reset() {
    clearRecordTimers();
    setResult(null);
    setError("");
    setElapsed(0);
    clearAudioSelection();
  }

  return (
    <main className="page">
      <p className="eyebrow">Interview practice</p>
      <h1>Hear how your introduction lands.</h1>
      <p className="lede">
        Upload a recording or speak one now, up to 3 minutes. The review comes back as a
        transcript, clarity notes, and the skills you actually mentioned.
      </p>

      <section className="panel">
        <div className="actions">
          <button
            className={`choice${source === "upload" ? " active" : ""}`}
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={busy || recording}
          >
            <strong>Upload audio</strong>
            <span>
              {source === "upload" && audioFile
                ? audioFile.name
                : "wav, mp3, m4a, or webm · max 3 min"}
            </span>
          </button>
          <button
            className={`choice${recording || source === "record" ? " active" : ""}`}
            type="button"
            onClick={toggleRecording}
            disabled={busy}
          >
            <strong>{recording ? "Stop recording" : "Record now"}</strong>
            <span>
              {recording
                ? `${formatClock(elapsed)} / 03:00`
                : source === "record"
                  ? "Recording ready to analyze"
                  : "Use your microphone · max 3 min"}
            </span>
          </button>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*,.wav,.mp3,.flac,.m4a,.webm,.ogg,.mp4"
          hidden
          onChange={onFileChange}
        />

        {recording && (
          <div className="recorder">
            <button className="record live" type="button" onClick={toggleRecording} aria-label="Stop recording" />
            <p className="record-label">
              Recording {formatClock(elapsed)}. Introductions stop automatically at 3 minutes.
            </p>
          </div>
        )}

        {audioUrl && (
          <audio className="preview" controls src={audioUrl} />
        )}

        <button className="primary" type="button" onClick={analyze} disabled={!audioFile || busy || recording}>
          {busy ? "Analyzing…" : "Analyze introduction"}
        </button>
        {audioFile && (
          <button className="ghost" type="button" onClick={reset} disabled={busy || recording}>
            Start over
          </button>
        )}
        {error && <p className="error">{error}</p>}
      </section>

      {result && (
        <section className="panel result">
          <div>
            <h2>Transcript</h2>
            <p>{result.transcript}</p>
          </div>
          <div>
            <h2>Clarity</h2>
            <p>{result.feedback.content_clarity}</p>
          </div>
          <div>
            <h2>What to improve</h2>
            <p>{result.feedback.feedback}</p>
          </div>
          <div>
            <h2>Skills</h2>
            <ChipList items={result.feedback.user_skills} />
          </div>
          <div>
            <h2>Character</h2>
            <ChipList items={result.feedback.user_character} />
          </div>
          <div>
            <h2>Sentiment</h2>
            <p>{result.feedback.sentiment}</p>
          </div>
        </section>
      )}
    </main>
  );
}

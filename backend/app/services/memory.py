import threading
import uuid
from typing import Dict, List, Optional


class SessionStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: Dict[str, List[Dict[str, str]]] = {}

    def ensure(self, session_id: Optional[str]) -> str:
        if session_id:
            return session_id
        new_id = str(uuid.uuid4())
        with self._lock:
            self._sessions[new_id] = []
        return new_id

    def history(self, session_id: str) -> List[Dict[str, str]]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def append(self, session_id: str, role: str, content: str) -> None:
        with self._lock:
            self._sessions.setdefault(session_id, []).append(
                {"role": role, "content": content}
            )


sessions = SessionStore()

import re
import time
from collections import defaultdict, deque
from threading import Lock

from app.config import settings


class AIGuardService:
    def __init__(self):
        self.user_hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()
        self.window_seconds = 60
        self.max_requests = 20

    def is_rate_limited(self, user_key: str) -> bool:
        if not user_key:
            return False
        now = time.time()
        cutoff = now - self.window_seconds
        with self._lock:
            queue = self.user_hits[user_key]
            while queue and queue[0] < cutoff:
                queue.popleft()
            if len(queue) >= self.max_requests:
                return True
            queue.append(now)
        return False

    def is_prompt_injection(self, text: str) -> bool:
        value = (text or "").lower()
        patterns = [
            "ignore previous instructions",
            "system prompt",
            "reveal hidden prompt",
            "bypass",
            "execute sql",
            "drop table",
            "admin password",
            "chave api",
            "api key",
            "token jwt",
        ]
        return any(p in value for p in patterns)

    def sanitize_user_input(self, text: str) -> str:
        value = (text or "").strip()
        value = re.sub(r"[^\S\r\n]{2,}", " ", value)
        return value[:2000]

    def sanitize_output(self, text: str) -> str:
        value = text or ""
        value = re.sub(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b", "[DADO_SENSIVEL]", value)
        value = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[EMAIL_OCULTO]", value)
        value = re.sub(r"\+?\d{10,15}", "[NUMERO_OCULTO]", value)
        return value


guard = AIGuardService()

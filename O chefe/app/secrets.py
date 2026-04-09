import json
import os
import time
from pathlib import Path

from app.config import settings


class SecretResolver:
    def __init__(self):
        self._cache: dict[str, str] = {}
        self._loaded_at = 0.0

    def _should_reload(self) -> bool:
        ttl = max(1, int(settings.secrets_reload_seconds))
        return (time.time() - self._loaded_at) > ttl

    def _load_file_secrets(self) -> dict[str, str]:
        path = Path(settings.secrets_file)
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return {}
            return {str(k): str(v) for k, v in data.items() if v is not None}
        except Exception:
            return {}

    def _reload(self) -> None:
        provider = (settings.secrets_provider or "env").lower().strip()
        if provider == "file":
            self._cache = self._load_file_secrets()
        else:
            self._cache = {}
        self._loaded_at = time.time()

    def get(self, key: str, fallback: str | None = None) -> str | None:
        if self._should_reload():
            self._reload()

        env_value = os.getenv(key)
        if env_value is not None and str(env_value).strip():
            return str(env_value).strip()

        if key in self._cache and self._cache[key].strip():
            return self._cache[key].strip()

        return fallback


resolver = SecretResolver()


def resolve_secret(key: str, fallback: str | None = None) -> str | None:
    return resolver.get(key=key, fallback=fallback)

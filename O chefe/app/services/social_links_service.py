import json
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings
from app.schemas import SocialLinksUpdate


class SocialLinksService:
    _keys = ("instagram", "facebook", "tiktok", "youtube")
    _branch_keys = ("instagram", "facebook", "tiktok", "youtube")
    _leadership_keys = ("instagram", "facebook", "tiktok", "youtube")

    def __init__(self):
        self.path = Path(settings.social_links_file)

    def _default(self) -> dict:
        return {
            "instagram": None,
            "facebook": None,
            "tiktok": None,
            "youtube": None,
            "branches": [],
            "leadership": [],
            "finance": {
                "pix_key": None,
                "pix_type": None,
                "holder_name": None,
                "note": None,
            },
            "updated_at": None,
        }

    def _normalize_url(self, value: str | None) -> str | None:
        if value is None:
            return None
        text = value.strip()
        if not text:
            return None
        if not text.startswith("http://") and not text.startswith("https://"):
            return f"https://{text}"
        return text

    def _normalize_branch(self, value: dict | None) -> dict | None:
        if not isinstance(value, dict):
            return None

        key = str(value.get("key") or "").strip() or None
        name = str(value.get("name") or "").strip() or None
        visit_note = str(value.get("visit_note") or "").strip() or None
        normalized = {
            "key": key,
            "name": name,
            "visit_note": visit_note,
            "instagram": None,
            "facebook": None,
            "tiktok": None,
            "youtube": None,
        }
        for social_key in self._branch_keys:
            normalized[social_key] = self._normalize_url(value.get(social_key))

        if not normalized["key"] and not normalized["name"]:
            return None
        return normalized

    def _normalize_leadership(self, value: dict | None) -> dict | None:
        if not isinstance(value, dict):
            return None

        role = str(value.get("role") or "").strip() or None
        name = str(value.get("name") or "").strip() or None
        normalized = {
            "role": role,
            "name": name,
            "instagram": None,
            "facebook": None,
            "tiktok": None,
            "youtube": None,
        }
        for social_key in self._leadership_keys:
            normalized[social_key] = self._normalize_url(value.get(social_key))

        if not normalized["role"] and not normalized["name"]:
            return None
        return normalized

    def _normalize_finance(self, value: dict | None) -> dict:
        data = value if isinstance(value, dict) else {}
        return {
            "pix_key": (str(data.get("pix_key") or "").strip() or None),
            "pix_type": (str(data.get("pix_type") or "").strip().lower() or None),
            "holder_name": (str(data.get("holder_name") or "").strip() or None),
            "note": (str(data.get("note") or "").strip() or None),
        }

    def get_links(self) -> dict:
        if not self.path.exists():
            return self._default()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            for key in self._keys:
                data.setdefault(key, None)
            branches = data.get("branches")
            if not isinstance(branches, list):
                branches = []
            normalized_branches = []
            for item in branches:
                normalized = self._normalize_branch(item)
                if normalized:
                    normalized_branches.append(normalized)
            data["branches"] = normalized_branches
            leadership = data.get("leadership")
            if not isinstance(leadership, list):
                leadership = []
            normalized_leadership = []
            for item in leadership:
                normalized = self._normalize_leadership(item)
                if normalized:
                    normalized_leadership.append(normalized)
            data["leadership"] = normalized_leadership
            data["finance"] = self._normalize_finance(data.get("finance"))
            data.setdefault("updated_at", None)
            return data
        except Exception:
            return self._default()

    def upsert_links(self, payload: SocialLinksUpdate) -> dict:
        current = self.get_links()
        incoming = payload.model_dump(exclude_unset=True)
        for key in self._keys:
            if key in incoming:
                current[key] = self._normalize_url(incoming[key])
        if "branches" in incoming:
            normalized_branches = []
            for item in incoming.get("branches") or []:
                normalized = self._normalize_branch(item)
                if normalized:
                    normalized_branches.append(normalized)
            current["branches"] = normalized_branches
        if "leadership" in incoming:
            normalized_leadership = []
            for item in incoming.get("leadership") or []:
                normalized = self._normalize_leadership(item)
                if normalized:
                    normalized_leadership.append(normalized)
            current["leadership"] = normalized_leadership
        if "finance" in incoming:
            current["finance"] = self._normalize_finance(incoming.get("finance"))
        current["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.path.write_text(json.dumps(current, indent=2), encoding="utf-8")
        return current

from __future__ import annotations

import re
import unicodedata

from app.constants import DEFAULT_UNITS, church_menu_text


class UnitResolverService:
    def __init__(self) -> None:
        self._menu_text = church_menu_text()
        self._normalized_units = {self._normalize(unit): unit for unit in DEFAULT_UNITS}

    def resolve(self, message: str, explicit_unit: str | None, member_unit: str | None) -> str | None:
        if explicit_unit:
            return explicit_unit
        if member_unit:
            return member_unit

        normalized_message = self._normalize(message)
        if normalized_message.isdigit():
            index = int(normalized_message)
            if 1 <= index <= len(DEFAULT_UNITS):
                return DEFAULT_UNITS[index - 1]

        for normalized_unit, original_unit in self._normalized_units.items():
            if normalized_unit in normalized_message:
                return original_unit

        return None

    def is_unit_only_message(self, message: str, unit: str | None) -> bool:
        if not unit:
            return False
        normalized_message = self._normalize(message)
        normalized_unit = self._normalize(unit)
        return normalized_message == normalized_unit or normalized_message in {str(index) for index in range(1, len(DEFAULT_UNITS) + 1)}

    def menu_text(self) -> str:
        return self._menu_text

    @staticmethod
    def confirmation_text(unit: str) -> str:
        return f"Perfeito. Você está falando com a {unit}. Agora envie sua dúvida ou solicitação."

    def _normalize(self, value: str) -> str:
        without_accents = "".join(
            character
            for character in unicodedata.normalize("NFKD", value)
            if not unicodedata.combining(character)
        )
        lowered = without_accents.lower().strip()
        lowered = re.sub(r"\s+", " ", lowered)
        return lowered

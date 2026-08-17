"""Safe ASCII filenames for accounting export downloads and ZIP members."""

from __future__ import annotations

import re
from typing import Optional

_UMLAUT_MAP: dict[str, str] = {
    "ä": "ae",
    "ö": "oe",
    "ü": "ue",
    "Ä": "Ae",
    "Ö": "Oe",
    "Ü": "Ue",
    "ß": "ss",
}


def safe_filename_stem(value: Optional[str], max_len: int = 40) -> str:
    """
    Build a Windows-/DATEV-safe filename stem: transliterate umlauts, ASCII only.
    """
    if not value:
        return ""
    transliterated: str = value.strip()
    for source, target in _UMLAUT_MAP.items():
        transliterated = transliterated.replace(source, target)
    cleaned: str = re.sub(r"[^\w\-]+", "_", transliterated, flags=re.ASCII)
    cleaned = re.sub(r"_+", "_", cleaned).strip("._")
    return cleaned[:max_len]

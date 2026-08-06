from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

logger: logging.Logger = logging.getLogger(__name__)


def read_xml_file_to_str(file_name: str) -> Optional[str]:
    """
    Read an XML fixture file and return it as a string.

    Resolves paths relative to cwd and to backend/tests/ so tests work
    whether pytest is started from backend/ or backend/tests/.
    """
    tests_root: Path = Path(__file__).resolve().parents[2] / "tests"
    candidates: List[Path] = [
        Path(file_name),
        Path.cwd() / file_name,
        tests_root / file_name,
        tests_root / "xml_files" / Path(file_name).name,
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8", errors="replace")

    logger.error(
        "File not found for '%s' (tried: %s)",
        file_name,
        [str(candidate) for candidate in candidates],
    )
    return None

"""Fail if forbidden legacy vendor/pipeline terms appear in the repo."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]

# Patterns are split so this file itself does not contain contiguous forbidden literals
# that would fail a naive whole-repo search of source text.
_CORE: list[str] = [
    "s" + "ixt",
    "high" + "way",
    "chro" + "nos",
    "com\\." + "sixt",
]
_EXTRA: list[str] = [
    r"\bHW-\d+",
    r"\bSWFM-\d+",
    r"\bM_IV_",
    r"\bM_CN_",
    r"\bM_IP_",
    r"\bS_KR_",
    "TRIGGER_" + "HIGHWAY",
    "SIXT_" + "VAT_ID",
    "HIGHWAY_" + "ZEITSTEMPEL",
    "format_" + "sixt" + "_number",
]

SKIP_DIR_NAMES: set[str] = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    ".pytest_cache",
    "egg-info",
    "xml_files",
    "pdf_files",
}

SKIP_FILE_NAMES: set[str] = {
    "anonymize_fixtures.py",
    "check_forbidden_terms.py",
}

ALLOWED_SUFFIXES: set[str] = {
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
    ".toml",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".css",
    ".html",
}


def _should_scan(path: Path) -> bool:
    if path.name in SKIP_FILE_NAMES:
        return False
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        return False
    for part in path.parts:
        if part in SKIP_DIR_NAMES or part.endswith(".egg-info"):
            return False
    return True


def main() -> int:
    combined: re.Pattern[str] = re.compile(
        "|".join(f"(?:{p})" for p in _CORE + _EXTRA),
        re.IGNORECASE,
    )
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or not _should_scan(path):
            continue
        try:
            text: str = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if combined.search(line):
                rel: str = str(path.relative_to(ROOT)).replace("\\", "/")
                hits.append(f"{rel}:{line_no}: {line.strip()[:200]}")

    if hits:
        print("Forbidden terms found:")
        for hit in hits:
            print(hit)
        return 1

    print("OK: no forbidden terms found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

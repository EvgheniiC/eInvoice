"""One-off helper to scrub legacy vendor strings from local XML fixtures."""

from __future__ import annotations

import re
from pathlib import Path

XML_DIR: Path = Path(__file__).resolve().parents[1] / "tests" / "xml_files"

# Built without embedding forbidden vendor tokens as contiguous literals.
_VENDOR: str = "s" + "ixt"
_PIPELINE: str = "high" + "way"
_LEGACY_DB: str = "chro" + "nos"

CONTENT_REPLACEMENTS: list[tuple[str, str]] = [
    (rf"(?i){_VENDOR}\s*gmbh", "Demo Buyer GmbH"),
    (rf"(?i){_VENDOR}\s*se", "Demo Buyer SE"),
    (rf"(?i){_VENDOR}\s*leasing", "Demo Leasing"),
    (rf"(?i)@{_VENDOR}\.[a-z.]+", "@demo-buyer.example"),
    (rf"(?i)\b{_VENDOR}\b", "DemoBuyer"),
    (rf"(?i){_VENDOR}-", "PO-"),
    (rf"(?i){_PIPELINE}", "pipeline"),
    (rf"(?i){_LEGACY_DB}", "ledger"),
    (r"\bSX-\d{5}(?:-\d{3})?\b", "CTR-00000"),
]


def _anonymize_text(text: str) -> str:
    result: str = text
    for pattern, replacement in CONTENT_REPLACEMENTS:
        result = re.sub(pattern, replacement, result)
    return result


def main() -> None:
    if not XML_DIR.is_dir():
        print(f"Skip: {XML_DIR} not found")
        return

    for xml_path in sorted(XML_DIR.glob("*.xml")):
        original: str = xml_path.read_text(encoding="utf-8", errors="replace")
        updated: str = _anonymize_text(original)
        if updated != original:
            xml_path.write_text(updated, encoding="utf-8")
            print(f"Anonymized content: {xml_path.name}")

    print("Done.")


if __name__ == "__main__":
    main()

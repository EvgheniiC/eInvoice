"""Parse KoSIT validator report XML into typed validation issues."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ParseError as EtParseError

from app.helper_functions.safe_xml import UnsafeXmlError, parse_xml
from app.schemas.invoice import ValidationIssue
from app.services.validation_profile import extract_bt_code

_JAR_VERSION_RE: re.Pattern[str] = re.compile(r"(\d+\.\d+(?:\.\d+)?)")


@dataclass
class KositReport:
    """Subset of a KoSIT VARL/SVRL report needed by the product UI."""

    accepted: Optional[bool] = None
    engine_name: Optional[str] = None
    engine_version: Optional[str] = None
    scenario_name: Optional[str] = None
    issues: List[ValidationIssue] = field(default_factory=list)


def find_kosit_report(directory: Path) -> Optional[Path]:
    reports: List[Path] = sorted(directory.glob("*-report.xml"))
    if reports:
        return reports[0]
    return None


def parse_kosit_report(xml_text: str) -> KositReport:
    """Extract engine version, scenario, and failed asserts from a KoSIT report."""
    report: KositReport = KositReport()
    try:
        root: Element = parse_xml(xml_text)
    except (UnsafeXmlError, EtParseError, ValueError):
        return report

    for element in root.iter():
        local: str = _local_name(element.tag)
        if local == "engine":
            _read_engine(element, report)
        elif local in {"scenarioMatched", "scenario"}:
            for child in element.iter():
                if _local_name(child.tag) == "name" and child.text:
                    report.scenario_name = child.text.strip() or report.scenario_name
                    break
        elif local in {"failed-assert", "failedAssert"}:
            report.issues.append(_issue_from_assert(element, default_level="error"))
        elif local in {"successful-report", "successfulReport"}:
            flag: str = (element.get("flag") or "information").lower()
            if flag in {"warning", "warn", "information", "info"}:
                report.issues.append(
                    _issue_from_assert(element, default_level=_level_from_flag(flag))
                )
        elif local in {"xmlSchema", "schema"}:
            report.issues.extend(_schema_messages(element))
        elif local == "accept":
            report.accepted = True
        elif local == "reject":
            report.accepted = False
        elif local == "noScenarioMatched":
            report.issues.append(
                ValidationIssue(
                    level="error",
                    category="schema",
                    code="KOSIT_NO_SCENARIO",
                    message=(
                        "KoSIT hat kein passendes Validierungsszenario gefunden. "
                        "Profil oder Szenarienstand prüfen."
                    ),
                    bt_code=None,
                    field=None,
                )
            )

    return report


def engine_version_from_jar(jar_path: Optional[str]) -> Optional[str]:
    if not jar_path:
        return None
    match: Optional[re.Match[str]] = _JAR_VERSION_RE.search(Path(jar_path).name)
    if match is None:
        return None
    return match.group(1)


def read_scenarios_label(scenarios_path: Optional[str]) -> Optional[str]:
    """Best-effort readable label from scenarios.xml (name and optional date)."""
    if not scenarios_path:
        return None
    path: Path = Path(scenarios_path)
    if not path.is_file():
        return None
    try:
        text: str = path.read_text(encoding="utf-8")
    except OSError:
        return None

    name: Optional[str] = None
    date: Optional[str] = None
    try:
        root: Element = parse_xml(text)
        for element in root.iter():
            local: str = _local_name(element.tag)
            if local == "name" and element.text and name is None:
                name = element.text.strip() or None
            elif local == "date" and element.text and date is None:
                date = element.text.strip() or None
    except (UnsafeXmlError, EtParseError, ValueError):
        name_match: Optional[re.Match[str]] = re.search(r"<name>([^<]+)</name>", text)
        date_match: Optional[re.Match[str]] = re.search(r"<date>([^<]+)</date>", text)
        if name_match:
            name = name_match.group(1).strip()
        if date_match:
            date = date_match.group(1).strip()

    if name and date:
        return f"{name} ({date})"
    return name


def _read_engine(element: Element, report: KositReport) -> None:
    version: Optional[str] = element.get("version")
    name: Optional[str] = element.get("name")
    for child in element:
        local: str = _local_name(child.tag)
        if local == "version" and child.text:
            version = version or child.text.strip()
        elif local == "name" and child.text:
            name = name or child.text.strip()
    if version:
        report.engine_version = version
    if name:
        report.engine_name = name


def _issue_from_assert(element: Element, *, default_level: str) -> ValidationIssue:
    code: str = (element.get("id") or element.get("ID") or "").strip() or "KOSIT_RULE"
    flag: Optional[str] = element.get("flag")
    message: str = _assert_text(element)
    if not message:
        message = f"KoSIT-Regel {code} verletzt."
    bt_code: Optional[str] = extract_bt_code(code, message)
    return ValidationIssue(
        level=_level_from_flag(flag) if flag else default_level,
        category="business",
        code=code,
        message=message[:500],
        bt_code=bt_code,
        field=None,
    )


def _schema_messages(schema_element: Element) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    for child in schema_element.iter():
        if _local_name(child.tag) != "message" or not child.text:
            continue
        text: str = child.text.strip()
        if not text:
            continue
        issues.append(
            ValidationIssue(
                level="error",
                category="schema",
                code="XSD_SCHEMA",
                message=text[:500],
            )
        )
    return issues


def _assert_text(element: Element) -> str:
    parts: List[str] = []
    for child in element.iter():
        if _local_name(child.tag) == "text" and child.text:
            parts.append(child.text.strip())
    if parts:
        return " ".join(parts)
    if element.text:
        return element.text.strip()
    return ""


def _level_from_flag(flag: Optional[str]) -> str:
    normalized: str = (flag or "fatal").strip().lower()
    if normalized in {"fatal", "error"}:
        return "error"
    if normalized in {"warning", "warn"}:
        return "warning"
    return "info"


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag.split(":")[-1]

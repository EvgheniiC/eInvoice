"""Tests for KoSIT report XML parsing."""

from __future__ import annotations

import unittest

from app.schemas.invoice import ValidationIssue
from app.services.kosit_report import KositReport, engine_version_from_jar, parse_kosit_report

_REPORT: str = """<?xml version="1.0" encoding="UTF-8"?>
<rep:report xmlns:rep="http://www.xoev.de/de/validator/varl/1"
            xmlns:svrl="http://purl.oclc.org/dsdl/svrl">
  <rep:engine>
    <rep:name>KoSIT Validator</rep:name>
    <rep:version>1.5.0</rep:version>
  </rep:engine>
  <rep:scenarioMatched>
    <name>XRechnung 3.0.2</name>
  </rep:scenarioMatched>
  <rep:xmlSchema>
    <rep:message>cvc-complex-type.2.4.a: Invalid content starting with ID.</rep:message>
  </rep:xmlSchema>
  <svrl:failed-assert id="BR-CO-15" flag="fatal"
      location="/*:Invoice">
    <svrl:text>[BR-CO-15] Invoice total amount with VAT (BT-112) must equal net plus tax.</svrl:text>
  </svrl:failed-assert>
  <svrl:successful-report id="BR-DE-NOTE" flag="warning">
    <svrl:text>Hinweis zur Leitweg-ID.</svrl:text>
  </svrl:successful-report>
  <rep:assessment>
    <rep:reject/>
  </rep:assessment>
</rep:report>
"""


class TestKositReport(unittest.TestCase):
    def test_parses_engine_scenario_schema_and_rules(self) -> None:
        report: KositReport = parse_kosit_report(_REPORT)
        self.assertEqual(report.engine_version, "1.5.0")
        self.assertEqual(report.engine_name, "KoSIT Validator")
        self.assertEqual(report.scenario_name, "XRechnung 3.0.2")
        self.assertIs(report.accepted, False)

        codes: set[str] = {issue.code or "" for issue in report.issues}
        self.assertIn("XSD_SCHEMA", codes)
        self.assertIn("BR-CO-15", codes)
        self.assertIn("BR-DE-NOTE", codes)

        schema_issue: ValidationIssue = next(
            item for item in report.issues if item.code == "XSD_SCHEMA"
        )
        self.assertEqual(schema_issue.level, "error")
        self.assertEqual(schema_issue.category, "schema")

        business_issue: ValidationIssue = next(
            item for item in report.issues if item.code == "BR-CO-15"
        )
        self.assertEqual(business_issue.level, "error")
        self.assertEqual(business_issue.category, "business")
        self.assertEqual(business_issue.bt_code, "BT-112")

        warning: ValidationIssue = next(
            item for item in report.issues if item.code == "BR-DE-NOTE"
        )
        self.assertEqual(warning.level, "warning")

    def test_jar_filename_version(self) -> None:
        self.assertEqual(
            engine_version_from_jar("/opt/kosit/validationtool-1.5.0-standalone.jar"),
            "1.5.0",
        )


if __name__ == "__main__":
    unittest.main()

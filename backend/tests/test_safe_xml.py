"""XXE / entity-bomb hardening tests."""

from __future__ import annotations

import unittest
from xml.etree.ElementTree import ParseError

from app.helper_functions.safe_xml import UnsafeXmlError, parse_xml
from app.services.invoice_service import InvoiceService


class SafeXmlTests(unittest.TestCase):
    def test_rejects_doctype_xxe(self) -> None:
        payload: str = (
            '<?xml version="1.0"?>\n'
            '<!DOCTYPE foo [\n'
            '  <!ENTITY xxe SYSTEM "file:///etc/passwd">\n'
            "]>\n"
            "<Invoice>&xxe;</Invoice>"
        )
        with self.assertRaises(UnsafeXmlError):
            parse_xml(payload)

    def test_rejects_entity_bomb(self) -> None:
        payload: str = (
            '<?xml version="1.0"?>\n'
            '<!DOCTYPE lolz [\n'
            '  <!ENTITY lol "lol">\n'
            '  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">\n'
            "]>\n"
            "<Invoice>&lol2;</Invoice>"
        )
        with self.assertRaises(UnsafeXmlError):
            parse_xml(payload)

    def test_parses_normal_invoice_root(self) -> None:
        payload: str = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100">'
            "<rsm:ExchangedDocument><ram:ID xmlns:ram="
            '"urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100">'
            "TEST-1</ram:ID></rsm:ExchangedDocument>"
            "</rsm:CrossIndustryInvoice>"
        )
        root = parse_xml(payload)
        self.assertTrue(root.tag.endswith("CrossIndustryInvoice"))

    def test_service_returns_unsafe_xml_code(self) -> None:
        payload: bytes = (
            b'<?xml version="1.0"?>\n'
            b'<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>\n'
            b"<Invoice>&xxe;</Invoice>"
        )
        result = InvoiceService().parse_upload("evil.xml", payload)
        self.assertEqual(result.status.value, "error")
        self.assertTrue(
            any(issue.code == "UNSAFE_XML" for issue in result.validation_issues)
        )

    def test_malformed_still_parse_error(self) -> None:
        with self.assertRaises(ParseError):
            parse_xml("<Invoice><broken>")


if __name__ == "__main__":
    unittest.main()

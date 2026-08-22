"""ZIP ingest: only .xml/.pdf, zip-bomb and zip-slip rejected."""

from __future__ import annotations

import io
import unittest
import zipfile

from app.helper_functions.safe_zip import (
    ZIP_BOMB_DETAIL,
    ZIP_EMPTY_DETAIL,
    ZIP_PATH_DETAIL,
    ZipIngestError,
    extract_invoice_files_from_zip,
)


def _zip_bytes(members: list[tuple[str, bytes]], *, compression: int = zipfile.ZIP_DEFLATED) -> bytes:
    buffer: io.BytesIO = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=compression) as archive:
        for name, payload in members:
            archive.writestr(name, payload)
    return buffer.getvalue()


class TestSafeZip(unittest.TestCase):
    def test_extracts_xml_and_pdf_from_nested_folders(self) -> None:
        content: bytes = _zip_bytes(
            [
                ("invoices/one.xml", b"<Invoice>1</Invoice>"),
                ("invoices/two.PDF", b"%PDF-1.4 test"),
                ("readme.txt", b"ignore"),
                ("__MACOSX/._one.xml", b"junk"),
            ]
        )
        files: list[tuple[str, bytes]] = extract_invoice_files_from_zip(
            content,
            max_files=20,
            max_file_bytes=1024 * 1024,
            max_uncompressed_bytes=2 * 1024 * 1024,
            max_ratio=100.0,
            max_listed_entries=200,
        )
        names: list[str] = [name for name, _ in files]
        self.assertEqual(names, ["one.xml", "two.PDF"])
        self.assertEqual(files[0][1], b"<Invoice>1</Invoice>")

    def test_rejects_path_traversal(self) -> None:
        content: bytes = _zip_bytes([("../secret.xml", b"<Invoice/>")])
        with self.assertRaises(ZipIngestError) as raised:
            extract_invoice_files_from_zip(
                content,
                max_files=20,
                max_file_bytes=1024 * 1024,
                max_uncompressed_bytes=2 * 1024 * 1024,
                max_ratio=100.0,
                max_listed_entries=200,
            )
        self.assertEqual(str(raised.exception), ZIP_PATH_DETAIL)

    def test_rejects_high_compression_ratio(self) -> None:
        inflated: bytes = b"<?xml version='1.0'?><Invoice>" + (b"0" * 200_000) + b"</Invoice>"
        content: bytes = _zip_bytes([("bomb.xml", inflated)])
        with self.assertRaises(ZipIngestError) as raised:
            extract_invoice_files_from_zip(
                content,
                max_files=20,
                max_file_bytes=1024 * 1024,
                max_uncompressed_bytes=2 * 1024 * 1024,
                max_ratio=20.0,
                max_listed_entries=200,
            )
        self.assertEqual(str(raised.exception), ZIP_BOMB_DETAIL)

    def test_nested_zip_only_is_empty(self) -> None:
        inner: bytes = _zip_bytes([("one.xml", b"<Invoice/>")])
        content: bytes = _zip_bytes([("pack.zip", inner)])
        with self.assertRaises(ZipIngestError) as raised:
            extract_invoice_files_from_zip(
                content,
                max_files=20,
                max_file_bytes=1024 * 1024,
                max_uncompressed_bytes=2 * 1024 * 1024,
                max_ratio=100.0,
                max_listed_entries=200,
            )
        self.assertEqual(str(raised.exception), ZIP_EMPTY_DETAIL)

    def test_duplicate_basenames_get_suffix(self) -> None:
        content: bytes = _zip_bytes(
            [
                ("a/one.xml", b"<Invoice>a</Invoice>"),
                ("b/one.xml", b"<Invoice>b</Invoice>"),
            ]
        )
        files: list[tuple[str, bytes]] = extract_invoice_files_from_zip(
            content,
            max_files=20,
            max_file_bytes=1024 * 1024,
            max_uncompressed_bytes=2 * 1024 * 1024,
            max_ratio=100.0,
            max_listed_entries=200,
        )
        self.assertEqual([name for name, _ in files], ["one.xml", "one_2.xml"])


if __name__ == "__main__":
    unittest.main()

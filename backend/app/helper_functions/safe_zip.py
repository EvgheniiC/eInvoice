"""Bounded ZIP ingest for batch upload: only .xml/.pdf, reject zip-bombs and zip-slip."""

from __future__ import annotations

import io
import stat
import zipfile
from pathlib import Path
from typing import Optional

INVOICE_SUFFIXES: frozenset[str] = frozenset({".xml", ".pdf"})
ALLOWED_COMPRESS: frozenset[int] = frozenset({zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED})
ZIP_ENCRYPTED_FLAG: int = 0x1
READ_CHUNK_BYTES: int = 65536

ZIP_CORRUPT_DETAIL: str = "ZIP-Datei ist beschädigt oder kein gültiges Archiv."
ZIP_ENCRYPTED_DETAIL: str = "Verschlüsselte ZIP-Dateien werden nicht unterstützt."
ZIP_BOMB_DETAIL: str = (
    "ZIP-Datei ist zu groß oder entpackt sich zu stark (Schutz vor ZIP-Bomben)."
)
ZIP_EMPTY_DETAIL: str = "ZIP enthält keine XML- oder PDF-Dateien."
ZIP_PATH_DETAIL: str = "ZIP enthält ungültige Pfade."
ZIP_SYMLINK_DETAIL: str = "ZIP mit symbolischen Links wird nicht unterstützt."
ZIP_TOO_MANY_LISTED_DETAIL: str = "ZIP enthält zu viele Einträge."
ZIP_UNSUPPORTED_COMPRESS_DETAIL: str = (
    "ZIP verwendet ein nicht unterstütztes Kompressionsverfahren."
)


class ZipIngestError(ValueError):
    """German user-facing ZIP rejection."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.detail: str = message


def extract_invoice_files_from_zip(
    content: bytes,
    *,
    max_files: int,
    max_file_bytes: int,
    max_uncompressed_bytes: int,
    max_ratio: float,
    max_listed_entries: int,
) -> list[tuple[str, bytes]]:
    """
    Return (filename, bytes) for invoice members only.

    Inspects ZipInfo sizes before reading. Skips directories, junk, and nested ZIPs.
    """
    if not content:
        raise ZipIngestError(ZIP_CORRUPT_DETAIL)
    try:
        archive: zipfile.ZipFile = zipfile.ZipFile(io.BytesIO(content), mode="r")
    except zipfile.BadZipFile as exc:
        raise ZipIngestError(ZIP_CORRUPT_DETAIL) from exc

    with archive:
        try:
            infos: list[zipfile.ZipInfo] = archive.infolist()
        except zipfile.BadZipFile as exc:
            raise ZipIngestError(ZIP_CORRUPT_DETAIL) from exc
        if len(infos) > max_listed_entries:
            raise ZipIngestError(ZIP_TOO_MANY_LISTED_DETAIL)
        _assert_archive_budget(infos, max_uncompressed_bytes=max_uncompressed_bytes)
        payloads: list[tuple[str, bytes]] = []
        used_names: set[str] = set()
        for info in infos:
            extracted: Optional[tuple[str, bytes]] = _extract_invoice_member(
                archive,
                info,
                max_file_bytes=max_file_bytes,
                max_ratio=max_ratio,
                used_names=used_names,
            )
            if extracted is None:
                continue
            payloads.append(extracted)
            if len(payloads) > max_files:
                raise ZipIngestError(
                    f"ZIP enthält mehr als {max_files} Rechnungsdateien."
                )
        if not payloads:
            raise ZipIngestError(ZIP_EMPTY_DETAIL)
        return payloads


def _assert_archive_budget(
    infos: list[zipfile.ZipInfo],
    *,
    max_uncompressed_bytes: int,
) -> None:
    total_uncompressed: int = 0
    for info in infos:
        if info.is_dir():
            continue
        file_size: int = max(0, int(info.file_size))
        if file_size > max_uncompressed_bytes:
            raise ZipIngestError(ZIP_BOMB_DETAIL)
        total_uncompressed += file_size
        if total_uncompressed > max_uncompressed_bytes:
            raise ZipIngestError(ZIP_BOMB_DETAIL)


def _extract_invoice_member(
    archive: zipfile.ZipFile,
    info: zipfile.ZipInfo,
    *,
    max_file_bytes: int,
    max_ratio: float,
    used_names: set[str],
) -> Optional[tuple[str, bytes]]:
    if info.is_dir():
        return None
    if info.flag_bits & ZIP_ENCRYPTED_FLAG:
        raise ZipIngestError(ZIP_ENCRYPTED_DETAIL)
    if _is_symlink(info):
        raise ZipIngestError(ZIP_SYMLINK_DETAIL)
    if info.compress_type not in ALLOWED_COMPRESS:
        raise ZipIngestError(ZIP_UNSUPPORTED_COMPRESS_DETAIL)
    raw_name: str = info.filename or ""
    if _is_unsafe_zip_path(raw_name):
        raise ZipIngestError(ZIP_PATH_DETAIL)
    filename: Optional[str] = _invoice_member_filename(raw_name)
    if filename is None:
        return None
    _assert_member_size(info, max_file_bytes=max_file_bytes, max_ratio=max_ratio)
    data: bytes = _read_member_bounded(archive, info, max_file_bytes=max_file_bytes)
    if len(data) == 0:
        return None
    unique_name: str = _unique_filename(filename, used_names)
    return unique_name, data


def _assert_member_size(
    info: zipfile.ZipInfo,
    *,
    max_file_bytes: int,
    max_ratio: float,
) -> None:
    file_size: int = max(0, int(info.file_size))
    compress_size: int = max(0, int(info.compress_size))
    if file_size > max_file_bytes:
        raise ZipIngestError(ZIP_BOMB_DETAIL)
    if compress_size == 0:
        if file_size > 0 and info.compress_type != zipfile.ZIP_STORED:
            raise ZipIngestError(ZIP_BOMB_DETAIL)
        return
    ratio: float = file_size / compress_size
    if ratio > max_ratio:
        raise ZipIngestError(ZIP_BOMB_DETAIL)


def _read_member_bounded(
    archive: zipfile.ZipFile,
    info: zipfile.ZipInfo,
    *,
    max_file_bytes: int,
) -> bytes:
    declared: int = max(0, int(info.file_size))
    limit: int = min(max_file_bytes, declared if declared > 0 else max_file_bytes)
    chunks: list[bytes] = []
    total: int = 0
    try:
        handle = archive.open(info, "r")
    except (RuntimeError, zipfile.BadZipFile) as exc:
        message: str = str(exc).lower()
        if "encrypted" in message or "password" in message:
            raise ZipIngestError(ZIP_ENCRYPTED_DETAIL) from exc
        raise ZipIngestError(ZIP_CORRUPT_DETAIL) from exc
    with handle:
        while True:
            chunk: bytes = handle.read(READ_CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                raise ZipIngestError(ZIP_BOMB_DETAIL)
            chunks.append(chunk)
    return b"".join(chunks)


def _invoice_member_filename(raw_name: str) -> Optional[str]:
    normalized: str = raw_name.replace("\\", "/")
    parts: list[str] = [part for part in normalized.split("/") if part]
    if any(part == "__MACOSX" for part in parts):
        return None
    base: str = Path(normalized).name
    if not base or base in {".", ".."}:
        return None
    if base.startswith(".") or base.startswith("._"):
        return None
    suffix: str = Path(base).suffix.lower()
    if suffix not in INVOICE_SUFFIXES:
        return None
    return base[:255]


def _is_unsafe_zip_path(raw_name: str) -> bool:
    normalized: str = raw_name.replace("\\", "/")
    if normalized.startswith("/") or normalized.startswith("\\"):
        return True
    if len(normalized) >= 2 and normalized[1] == ":":
        return True
    parts: list[str] = [part for part in normalized.split("/") if part]
    return any(part == ".." for part in parts)


def _is_symlink(info: zipfile.ZipInfo) -> bool:
    mode: int = info.external_attr >> 16
    if mode == 0:
        return False
    return stat.S_ISLNK(mode)


def _unique_filename(name: str, used_names: set[str]) -> str:
    if name not in used_names:
        used_names.add(name)
        return name
    stem: str = Path(name).stem
    suffix: str = Path(name).suffix
    index: int = 2
    while True:
        candidate: str = f"{stem}_{index}{suffix}"
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate
        index += 1

from typing import List, Protocol, runtime_checkable


@runtime_checkable
class InvoiceLogger(Protocol):
    """Logging contract used by invoice parsers (info / error)."""

    def info_log(self, message: str) -> None:
        ...

    def error_log(self, message: str) -> None:
        ...


class ServiceLogger:
    """Minimal logger adapter matching the InvoiceLogger interface."""

    def __init__(self) -> None:
        self.messages: List[str] = []

    def info_log(self, message: str) -> None:
        self.messages.append(f"INFO: {message}")

    def error_log(self, message: str) -> None:
        self.messages.append(f"ERROR: {message}")

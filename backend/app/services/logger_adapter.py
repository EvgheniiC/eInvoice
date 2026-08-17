from typing import Protocol, runtime_checkable


@runtime_checkable
class InvoiceLogger(Protocol):
    """Logging contract used by invoice parsers (info / error)."""

    def info_log(self, message: str) -> None:
        ...

    def error_log(self, message: str) -> None:
        ...


class ServiceLogger:
    """Parser logger that never writes invoice content to application logs."""

    def info_log(self, message: str) -> None:
        return

    def error_log(self, message: str) -> None:
        return

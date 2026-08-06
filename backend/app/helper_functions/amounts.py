from __future__ import annotations

from typing import Optional, Union


def create_viable_float_or_int_string(
    value: str, de_format: bool = False
) -> Union[float, int, None, str]:
    """
    Normalize a numeric string by fixing comma/dot separators.
    """
    if de_format:
        value = value.replace(".", "")
        return float(value.replace(",", "."))

    value = value.replace(",", ".")
    if value.count(".") == 1:
        return value

    split_value: list[str] = value.split(".")
    if len(split_value) > 0:
        if len(split_value[-1]) < 3:
            normalized: str = value.replace(",", ".")
            return normalized.replace(".", "", normalized.count(".") - 1)
        return value.replace(",", ".").replace(".", "")
    return None


def string_to_float(
    value: Optional[Union[str, float, int]], de_format: bool = False
) -> Union[float, int, None, str]:
    """
    Convert a value to float. Returns 0 if not numeric, None if value is None.
    """
    if value is None:
        return None
    if not str(value).replace(",", "").replace(".", "").replace("-", "").strip().isdigit():
        return 0
    if isinstance(value, (float, int)):
        return value
    return float(create_viable_float_or_int_string(str(value).replace("-", ""), de_format))


def string_to_float_negative(
    value: Optional[Union[str, float, int]], de_format: bool = False
) -> Union[float, int, None, str]:
    """
    Convert a value to float while preserving a leading minus for line items.
    """
    if value is None:
        return None
    if not str(value).replace(",", "").replace(".", "").replace("-", "").strip().isdigit():
        return 0
    if isinstance(value, (float, int)):
        return value
    return float(create_viable_float_or_int_string(str(value), de_format))


def make_amount_non_negative(value: Optional[Union[str, float, int]]) -> Optional[float]:
    """
    Parse a monetary value and return its absolute value as a non-negative float.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return abs(float(value))
    stripped: str = str(value).strip()
    if not stripped:
        return None
    parsed: Union[float, int, None, str] = string_to_float(stripped)
    if parsed is None:
        return None
    if isinstance(parsed, str):
        try:
            normalized: float = float(parsed.replace(",", ".").replace(" ", ""))
        except ValueError:
            return None
        return abs(normalized)
    return abs(float(parsed))


def normalize_header_amount(value: Optional[Union[str, float, int]]) -> Optional[float]:
    """Parse and normalize a header monetary value to a non-negative float (2 decimals)."""
    amount: Optional[float] = make_amount_non_negative(value)
    if amount is None:
        return None
    return round(amount, 2)


def format_header_amount_string(value: Optional[float]) -> Optional[str]:
    """
    Format a float as a display/API string.
    Whole numbers are serialized without a fractional part (e.g. 1225 -> "1225").
    """
    if value is None:
        return None
    rounded: float = round(value, 2)
    if rounded == int(rounded):
        return str(int(rounded))
    return format(rounded, ".2f")


def optional_string_to_float(value: Optional[str]) -> Optional[float]:
    """Convert a non-empty numeric string to float; None stays None."""
    if value is None:
        return None
    stripped: str = value.strip()
    if not stripped:
        return None
    parsed: Union[float, int, None, str] = string_to_float(stripped)
    if parsed is None or isinstance(parsed, str):
        return None
    return float(parsed)

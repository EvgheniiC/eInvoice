from __future__ import annotations

import logging
from typing import Dict, List, Optional
from xml.etree.ElementTree import Element

logger: logging.Logger = logging.getLogger(__name__)


def find_tax_data(
    root: Element,
    json_config_paths: List[str],
    tax_name: str,
    max_rates: int = 5,
) -> Dict[str, Optional[str]]:
    """
    Find unique tax values for the given XPath list.

    Always returns exactly max_rates entries (missing ones are None).
    """
    percent_values: List[str] = []
    seen_values: set[str] = set()

    for path in json_config_paths:
        try:
            elements: List[Element] = root.findall(path)
            for elem in elements:
                if elem.text:
                    value: str = str(elem.text.strip())
                    if value not in seen_values:
                        percent_values.append(value)
                        seen_values.add(value)
                        if len(percent_values) >= max_rates:
                            break
            if len(percent_values) >= max_rates:
                break
        except Exception as exc:
            logger.warning("Could not process path %s: %s", path, exc)
            continue

    tax_rates: Dict[str, Optional[str]] = {}
    for index in range(1, max_rates + 1):
        if index <= len(percent_values):
            tax_rates[f"{tax_name}{index}"] = percent_values[index - 1]
        else:
            tax_rates[f"{tax_name}{index}"] = None
    return tax_rates

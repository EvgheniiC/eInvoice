from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

logger: logging.Logger = logging.getLogger(__name__)

_CONFIG_DIR: Path = Path(__file__).resolve().parent / "config"


@lru_cache(maxsize=1)
def load_mappings() -> Dict[str, str]:
    """Load and cache attribute mappings from mapping_client.json."""
    config_path: Path = _CONFIG_DIR / "mapping_client.json"
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            data: Dict[str, Any] = json.load(file)
            mappings: Any = data.get("attribute_mappings", {})
            if isinstance(mappings, dict):
                return {str(key): str(value) for key, value in mappings.items()}
            return {}
    except FileNotFoundError as exc:
        logger.warning("Config file not found: %s", exc)
        return {}
    except json.JSONDecodeError as exc:
        logger.warning("Error parsing JSON: %s", exc)
        return {}


@lru_cache(maxsize=1)
def _load_tags_json() -> Dict[str, List[str]]:
    """Load and cache the full tags.json dictionary."""
    json_file_with_tags: Path = _CONFIG_DIR / "tags.json"
    if not json_file_with_tags.is_file():
        logger.warning("File %s not found.", json_file_with_tags)
        return {}
    with open(json_file_with_tags, encoding="utf-8") as file:
        json_data: Any = json.load(file)
    if not isinstance(json_data, dict):
        return {}
    result: Dict[str, List[str]] = {}
    for key, value in json_data.items():
        if isinstance(value, list):
            result[str(key)] = [str(item) for item in value]
    return result


def get_tags_from_json(tag: str) -> List[str]:
    """Return a copy of XPath tags for the given config key."""
    return list(_load_tags_json().get(tag, []))


@lru_cache(maxsize=1)
def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Load field configuration from a JSON file.

    Relative paths are resolved against the helper_functions directory.
    """
    path: Path = Path(config_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / config_path

    if not path.exists():
        logger.warning("Config file %s not found!", path)
        return {}

    with open(path, "r", encoding="utf-8") as file:
        config: Dict[str, Any] = json.load(file)
    fields: Any = config.get("fields", config)
    return fields if isinstance(fields, dict) else {}

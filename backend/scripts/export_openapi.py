"""Dump the live FastAPI OpenAPI schema and matching TypeScript DTO types."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT: Path = Path(__file__).resolve().parents[1]
REPO_ROOT: Path = BACKEND_ROOT.parent
OPENAPI_PATH: Path = REPO_ROOT / "frontend" / "openapi.json"
TYPES_PATH: Path = REPO_ROOT / "frontend" / "src" / "types" / "openapi.ts"

_IDENT_RE: re.Pattern[str] = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def build_openapi() -> dict[str, Any]:
    """Return the canonical OpenAPI document from the FastAPI application."""
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    from app.main import app

    return app.openapi()


def dump_openapi_text(schema: dict[str, Any]) -> str:
    """Serialize OpenAPI JSON with stable UTF-8 formatting."""
    return json.dumps(schema, indent=2, ensure_ascii=False) + "\n"


def render_typescript(openapi: dict[str, Any]) -> str:
    """Render TypeScript `components.schemas` types from an OpenAPI document."""
    schemas: dict[str, Any] = openapi.get("components", {}).get("schemas", {})
    lines: list[str] = [
        "/**",
        " * Generated from FastAPI OpenAPI by backend/scripts/export_openapi.py.",
        " * Do not edit by hand.",
        " */",
        "",
        "export interface components {",
        "  schemas: {",
    ]
    for name in sorted(schemas.keys()):
        ts_type: str = _emit_schema(schemas[name], indent=4)
        lines.append(f"    {_ts_key(name)}: {ts_type};")
    lines.extend(
        [
            "  };",
            "}",
            "",
        ]
    )
    return "\n".join(lines)


def write_openapi(openapi_path: Path = OPENAPI_PATH, types_path: Path = TYPES_PATH) -> None:
    """Write the live schema and generated TypeScript types to disk."""
    schema: dict[str, Any] = build_openapi()
    openapi_path.parent.mkdir(parents=True, exist_ok=True)
    types_path.parent.mkdir(parents=True, exist_ok=True)
    openapi_path.write_text(dump_openapi_text(schema), encoding="utf-8", newline="\n")
    types_path.write_text(render_typescript(schema), encoding="utf-8", newline="\n")


def check_openapi(openapi_path: Path = OPENAPI_PATH, types_path: Path = TYPES_PATH) -> None:
    """Exit with an error if committed snapshots do not match FastAPI."""
    live: dict[str, Any] = build_openapi()
    expected_ts: str = render_typescript(live)
    if not openapi_path.is_file() or not types_path.is_file():
        raise SystemExit(
            "Missing OpenAPI snapshot files.\n"
            "Generate them with: python backend/scripts/export_openapi.py"
        )
    committed: Any = json.loads(openapi_path.read_text(encoding="utf-8"))
    committed_ts: str = types_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if committed != live or committed_ts != expected_ts:
        raise SystemExit(
            "API contract snapshots are out of date with FastAPI DTOs.\n"
            "Regenerate with: python backend/scripts/export_openapi.py"
        )


def _ts_key(name: str) -> str:
    if _IDENT_RE.match(name):
        return name
    return json.dumps(name)


def _emit_schema(schema: dict[str, Any], indent: int) -> str:
    if "$ref" in schema:
        ref_name: str = str(schema["$ref"]).rsplit("/", 1)[-1]
        return f'components["schemas"][{json.dumps(ref_name)}]'
    if "anyOf" in schema:
        return " | ".join(_emit_schema(item, indent) for item in schema["anyOf"])
    if "oneOf" in schema:
        return " | ".join(_emit_schema(item, indent) for item in schema["oneOf"])
    if "allOf" in schema:
        return " & ".join(_emit_schema(item, indent) for item in schema["allOf"])
    if "enum" in schema:
        return " | ".join(json.dumps(value) for value in schema["enum"])

    schema_type: Any = schema.get("type")
    if schema_type == "null":
        return "null"
    if schema_type == "string":
        return "string"
    if schema_type in {"integer", "number"}:
        return "number"
    if schema_type == "boolean":
        return "boolean"
    if schema_type == "array":
        items: dict[str, Any] = schema.get("items", {})
        inner: str = _emit_schema(items, indent)
        if " | " in inner or " & " in inner:
            return f"({inner})[]"
        return f"{inner}[]"
    if schema_type == "object" or "properties" in schema:
        return _emit_object(schema, indent)
    return "unknown"


def _emit_object(schema: dict[str, Any], indent: int) -> str:
    properties: dict[str, Any] = schema.get("properties") or {}
    if not properties:
        return "Record<string, unknown>"
    required: set[str] = set(schema.get("required") or [])
    inner_indent: str = " " * (indent + 2)
    close_indent: str = " " * indent
    lines: list[str] = ["{"]
    for name, prop_schema in properties.items():
        optional: str = "" if name in required else "?"
        ts_type: str = _emit_schema(prop_schema, indent + 2)
        lines.append(f"{inner_indent}{_ts_key(name)}{optional}: {ts_type};")
    lines.append(f"{close_indent}}}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Export or check the FastAPI OpenAPI snapshot and TypeScript types.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if committed OpenAPI/TypeScript files do not match the live schema.",
    )
    args: argparse.Namespace = parser.parse_args(argv)
    if args.check:
        check_openapi()
        return 0
    write_openapi()
    print(f"Wrote {OPENAPI_PATH}")
    print(f"Wrote {TYPES_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Ensure the committed OpenAPI snapshot matches live FastAPI DTOs."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


class TestOpenApiContract(unittest.TestCase):
    def test_committed_openapi_matches_fastapi_schema(self) -> None:
        script: Path = Path(__file__).resolve().parents[1] / "scripts" / "export_openapi.py"
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, str(script), "--check"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            self.fail(result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

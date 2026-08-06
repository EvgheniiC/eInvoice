import subprocess
import sys
import unittest
from pathlib import Path


class TestForbiddenTerms(unittest.TestCase):
    def test_repo_has_no_forbidden_legacy_terms(self) -> None:
        script: Path = Path(__file__).resolve().parents[1] / "scripts" / "check_forbidden_terms.py"
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            self.fail(result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

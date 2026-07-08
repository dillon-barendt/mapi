import json
import subprocess
import sys


def test_import_csv_cli_outputs_compact_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.cli",
            "import-csv",
            "examples/csv/demo_venue_rows.csv",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "sections": {
            "101": "AA:DD,A:C,8:19!,13=13W",
            "102": "A,2:3!,D",
        }
    }


def test_import_csv_cli_returns_nonzero_for_missing_file() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "app.cli", "import-csv", "missing.csv"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "error:" in result.stderr

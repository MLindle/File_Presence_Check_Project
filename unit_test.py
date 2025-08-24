import pytest
import subprocess
import sys
from pathlib import Path
import check_required_files


SCRIPT = Path(__file__).resolve().parent / "check_required_files.py"

def test_config_file_presence():
    assert (Path(__file__).resolve().parent / "check_required_files.py").is_file()

def test_file_presence(tmp_path):

    (tmp_path / ".required-files.yml").write_text("custom_file")

    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=tmp_path,           
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, (
        f"Expected 0, got {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
    )

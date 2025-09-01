import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_config import Colors, print_header, print_status


def test_colors_okgreen() -> None:
    assert Colors.OKGREEN == "\033[92m"


def test_print_status_with_details(capfd: pytest.CaptureFixture[str]) -> None:
    print_status("message", success=True, details="extra")
    out, _ = capfd.readouterr()
    assert "message" in out
    assert "extra" in out
    assert "✅" in out


def test_print_header_outputs(capfd: pytest.CaptureFixture[str]) -> None:
    print_header("Title")
    out, _ = capfd.readouterr()
    assert "Title" in out
    assert Colors.HEADER in out

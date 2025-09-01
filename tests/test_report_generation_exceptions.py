import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))

from generate_sprint_report import ReportGenerator, ReportGenerationError
import aiofiles


@pytest.mark.asyncio
async def test_generate_report_missing_file(tmp_path, monkeypatch) -> None:
    control = tmp_path / "project" / "demo" / "control"
    control.mkdir(parents=True)
    (tmp_path / "memory-bank").mkdir()
    async with aiofiles.open(tmp_path / "memory-bank" / "decisionLog.md", "w", encoding="utf-8") as f:
        await f.write("# log\nentry")
    async with aiofiles.open(control / "sprint.yaml", "w", encoding="utf-8") as f:
        await f.write("goal: test\n")
    monkeypatch.chdir(tmp_path)
    reporter = ReportGenerator("demo")
    with pytest.raises(ReportGenerationError):
        await reporter.generate_report()


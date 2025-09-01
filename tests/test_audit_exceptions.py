import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))

from audit_autonomous_actions import ActionsAuditor, AuditError


@pytest.mark.asyncio
async def test_run_audit_missing_workflow(tmp_path, monkeypatch) -> None:
    (tmp_path / "project" / "demo" / "control").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    auditor = ActionsAuditor("demo")
    with pytest.raises(AuditError):
        await auditor.run_audit()


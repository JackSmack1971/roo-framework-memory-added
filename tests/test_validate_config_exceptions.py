import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_config import ConfigValidator, ConfigValidationError


def test_invalid_yaml_raises(tmp_path, monkeypatch) -> None:
    control = tmp_path / "project" / "demo" / "control"
    control.mkdir(parents=True)
    (tmp_path / ".roomodes").write_text("mode\n")
    (control / "backlog.yaml").write_text("agents: []\n")
    (control / "sprint.yaml").write_text("invalid: [")
    (control / "capabilities.yaml").write_text("agents:\n- a\n")
    (control / "workflow-state.json").write_text("{}")
    (control / "quality-dashboard.json").write_text("{}")
    docs = tmp_path / "docs" / "contracts"
    docs.mkdir(parents=True)
    (docs / "backlog_v1.schema.json").write_text("{}")
    (docs / "workflow_state_v2.schema.json").write_text("{}")
    monkeypatch.chdir(tmp_path)
    validator = ConfigValidator("demo")
    with pytest.raises(ConfigValidationError):
        validator.run_validations()


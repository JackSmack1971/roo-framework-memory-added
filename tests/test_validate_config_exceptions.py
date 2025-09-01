import json
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_config import ConfigValidationError, ConfigValidator


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


@pytest.mark.parametrize(
    "roomodes_content",
    [
        "customModes:\n  - slug: a\n",
        json.dumps({"customModes": [{"slug": "a"}]}),
    ],
)
def test_cross_reference_capabilities(tmp_path, monkeypatch, roomodes_content) -> None:
    control = tmp_path / "project" / "demo" / "control"
    control.mkdir(parents=True)
    (tmp_path / ".roomodes").write_text(roomodes_content)
    (control / "capabilities.yaml").write_text("agents:\n- a\n")
    monkeypatch.chdir(tmp_path)
    validator = ConfigValidator("demo")
    validator._cross_reference_capabilities()
    assert validator.errors == 0


@pytest.mark.parametrize(
    "roomodes_content",
    [
        "customModes:\n  - slug: a\n",
        json.dumps({"customModes": [{"slug": "a"}]}),
    ],
)
def test_cross_reference_capabilities_missing(
    tmp_path, monkeypatch, roomodes_content
) -> None:
    control = tmp_path / "project" / "demo" / "control"
    control.mkdir(parents=True)
    (tmp_path / ".roomodes").write_text(roomodes_content)
    (control / "capabilities.yaml").write_text("agents:\n- a\n- b\n")
    monkeypatch.chdir(tmp_path)
    validator = ConfigValidator("demo")
    validator._cross_reference_capabilities()
    assert validator.errors == 1


import sys
from pathlib import Path

import pytest

# Ensure scripts directory is on path
sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))

from path_utils import InvalidProjectPathError, resolve_project_path


@pytest.mark.asyncio
async def test_resolve_project_path_valid() -> None:
    project_name = await resolve_project_path("sample-app")
    assert project_name == "sample-app"


@pytest.mark.asyncio
async def test_resolve_project_path_sanitizes() -> None:
    project_name = await resolve_project_path("../sample-app")
    assert project_name == "sample-app"


@pytest.mark.asyncio
async def test_resolve_project_path_invalid() -> None:
    with pytest.raises(InvalidProjectPathError):
        await resolve_project_path("non-existent")

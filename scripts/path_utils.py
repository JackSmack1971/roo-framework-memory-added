import asyncio
import os
from typing import Final


class InvalidProjectPathError(Exception):
    """Raised when the provided project path is invalid."""


async def resolve_project_path(project_name: str) -> str:
    """Sanitize and validate the project name.

    Args:
        project_name: Raw project name provided by the user.

    Returns:
        The sanitized project name.

    Raises:
        InvalidProjectPathError: If the project directory does not exist.
    """
    sanitized: Final[str] = os.path.basename(project_name)
    project_path = os.path.join("project", sanitized)
    exists = await asyncio.to_thread(os.path.isdir, project_path)
    if not exists:
        raise InvalidProjectPathError(
            f"Project path '{project_path}' does not exist."
        )
    return sanitized

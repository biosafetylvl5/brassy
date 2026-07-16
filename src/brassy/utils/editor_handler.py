"""Resolve and launch the user's preferred text editor (git-style)."""

from __future__ import annotations

import os
import shlex
import subprocess
from typing import TYPE_CHECKING, Any

from brassy.brassy import Settings

if TYPE_CHECKING:
    from pathlib import Path


def _git_core_editor() -> str | None:
    """
    Return the editor configured in git's ``core.editor`` setting, if any.

    Returns
    -------
    str | None
        The value of ``git config --get core.editor``, or ``None`` when git
        is unavailable or the setting is unset.
    """
    try:
        result = subprocess.run(
            ["git", "config", "--get", "core.editor"],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, FileNotFoundError):
        return None
    editor = result.stdout.strip()
    return editor or None


def resolve_editor(override: str | None = None) -> str:
    """
    Resolve which editor command to launch, in git-like priority order.

    The lookup order is:

    1. The ``override`` argument (typically from the ``--editor`` CLI flag).
    2. The ``default_editor`` setting in the brassy configuration file.
    3. The ``VISUAL`` environment variable.
    4. The ``EDITOR`` environment variable.
    5. The ``core.editor`` setting from the git configuration.
    6. A platform default: ``notepad`` on Windows, ``vi`` elsewhere.

    Parameters
    ----------
    override : str | None
        An editor command supplied by the caller. When provided and non-empty,
        it takes precedence over every other source. ``None`` or an empty
        string is ignored.

    Returns
    -------
    str
        The editor command to launch, never empty.
    """
    if override:
        return override
    candidates = [
        Settings.default_editor,
        os.environ.get("VISUAL"),
        os.environ.get("EDITOR"),
        _git_core_editor(),
    ]
    for candidate in candidates:
        if candidate:
            return candidate
    return "notepad" if os.name == "nt" else "vi"


def launch_editor(path: Path, editor: str, error_console: Any) -> int:
    """
    Launch ``editor`` on ``path`` in the foreground and return its exit code.

    The editor runs attached to the controlling terminal so that interactive
    editors such as ``vim`` or ``nano`` function correctly. The ``editor``
    string is split with :func:`shlex.split` so that flags (e.g.
    ``code --wait``) are honoured.

    Parameters
    ----------
    path : Path
        Path to the file the editor should open.
    editor : str
        The editor command (possibly with arguments) resolved by
        :func:`resolve_editor`.
    error_console : Any
        A Rich console used to report errors when the editor command cannot be
        executed.

    Returns
    -------
    int
        The exit code returned by the editor process. ``1`` is returned when
        the editor binary itself could not be found.
    """
    command = [*shlex.split(editor), str(path)]
    try:
        return subprocess.call(command)  # noqa: S603
    except FileNotFoundError:
        error_console.print(
            f"[bold red]Could not launch editor '[bold]{editor}[/]'. "
            "Is it installed and on your PATH?",
        )
        return 1


def open_file_in_editor(
    path: Path,
    error_console: Any,
    editor_override: str | None = None,
) -> int:
    """
    Resolve an editor and launch it on ``path``, returning the exit code.

    Parameters
    ----------
    path : Path
        Path to the file to open.
    error_console : Any
        A Rich console used for error reporting.
    editor_override : str | None
        Optional editor command that bypasses resolution. ``None`` ignores the
        argument and resolves the editor normally.

    Returns
    -------
    int
        The editor process exit code (``1`` if the editor could not launch).
    """
    editor = resolve_editor(editor_override)
    return launch_editor(path, editor, error_console)

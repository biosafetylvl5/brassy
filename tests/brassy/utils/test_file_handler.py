"""
Tests for brassy.utils.file_handler path resolution.

The CLI always passes a working directory, so the default branch of
get_yaml_template_path is only reachable through the library API -- which
the module docstring for brassy.utils.CLI explicitly supports.
"""

import sys
from pathlib import Path

# Ensure we can import from src/
ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    src = parent / "src"
    if src.is_dir():
        sys.path.insert(0, str(src))
        break

from brassy.utils.file_handler import get_yaml_template_path  # noqa: E402


def test_default_working_dir_resolves_against_cwd(tmp_path, monkeypatch):
    """working_dir=None must fall back to the current directory.

    The fallback calls Path.getcwd(), which does not exist -- the classmethod
    is Path.cwd() -- so the documented default raises AttributeError instead
    of resolving anything.
    """
    monkeypatch.chdir(tmp_path)

    assert get_yaml_template_path("note.yaml", working_dir=None) == (
        tmp_path / "note.yaml"
    )


def test_default_working_dir_returns_a_path(tmp_path, monkeypatch):
    """The fallback must produce a Path, not a str or None.

    Callers join and open the result, so a str would fail further away from
    the cause than it needs to.
    """
    monkeypatch.chdir(tmp_path)

    assert isinstance(get_yaml_template_path("note.yaml", working_dir=None), Path)

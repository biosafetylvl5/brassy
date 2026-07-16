"""
Tests for brassy.utils.settings_manager.

These cover two defects: config-file creation crashing when a parent directory
is missing, and a missing config file resetting settings from other tiers back
to their defaults.
"""

import sys
from pathlib import Path

import pytest
import yaml

# Ensure we can import from src/
ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    src = parent / "src"
    if src.is_dir():
        sys.path.insert(0, str(src))
        break

from brassy.utils import settings_manager  # noqa: E402


def test_create_config_file_creates_missing_parents(tmp_path):
    """Writing a config into a missing directory creates the directory.

    The parent was created with Path.makedirs, which does not exist, so any
    site/user config write raised AttributeError and broke ``--init``.
    """
    target = tmp_path / "nested" / "dir" / "brassy.config"

    settings_manager.create_config_file(target)

    assert target.is_file()
    with target.open() as f:
        written = yaml.safe_load(f)
    assert "use_color" in written


def test_missing_config_returns_empty_dict(tmp_path):
    """A missing config file contributes nothing, not a full default dump.

    Returning the defaults let a merge overwrite higher-precedence tiers, so a
    missing project file silently reset every setting the user had configured.
    """
    missing = tmp_path / "nope.config"

    result = settings_manager.read_config_file(missing, create_file_if_not_exist=False)

    assert result == {}


def test_empty_config_file_contributes_nothing(tmp_path):
    """A config file with no settings in it must merge like a missing one.

    An empty (or comments-only) YAML file loads as None, which used to reach
    SettingsTemplate(**None) and crash every brassy command at import time.
    """
    empty = tmp_path / "empty.config"
    empty.write_text("# just a comment\n")

    assert settings_manager.read_config_file(empty) == {}
    merged = settings_manager.merge_and_validate_config_files([empty])
    assert merged == {}


def test_non_mapping_config_file_raises_a_named_error(tmp_path):
    """A config file that is valid YAML but not a mapping must name itself.

    Without the guard this surfaced as a TypeError about ** unpacking, with
    no hint of which of the three config tiers was malformed.
    """
    bad = tmp_path / "list.config"
    bad.write_text("- just\n- a list\n")

    with pytest.raises(ValueError, match=r"list\.config"):
        settings_manager.read_config_file(bad)


def test_missing_higher_tier_does_not_reset_lower_tier(tmp_path):
    """Merging an absent file must preserve earlier files' overrides.

    This is the precedence contract the empty-dict fix protects: a present
    lower-precedence file, then an absent higher-precedence one.
    """
    present = tmp_path / "user.config"
    with present.open("w") as f:
        yaml.dump({"default_title": "FROM USER CONFIG"}, f)
    absent = tmp_path / "project.config"

    merged = settings_manager.merge_and_validate_config_files([present, absent])

    assert merged["default_title"] == "FROM USER CONFIG"

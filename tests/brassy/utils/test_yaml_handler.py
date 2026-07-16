"""
Tests for brassy.utils.yaml_handler.

Covers rejection of duplicate keys at every nesting level, the conversion of
PyYAML errors into ValueError, and the guards against false positives on
brassy's normal release-note shape.
"""

import re
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

from brassy.utils.yaml_handler import load_yaml  # noqa: E402

DUPLICATE_CATEGORY = """\
bug fix:
- title: 'First entry'
  description: 'first'
enhancement:
- title: 'Unrelated'
  description: 'unrelated'
bug fix:
- title: 'Second entry'
  description: 'second'
"""


def test_duplicate_top_level_key_raises():
    """A category declared twice is rejected rather than silently dropped."""
    with pytest.raises(ValueError, match="Duplicate key") as exc_info:
        load_yaml(DUPLICATE_CATEGORY, "notes.yaml")
    message = str(exc_info.value)
    assert "notes.yaml" in message
    assert "Duplicate key 'bug fix'" in message
    assert "on line 7" in message  # the offending repeat
    assert "first defined on line 1" in message


def test_duplicate_top_level_key_would_lose_data_under_safe_load():
    """Guard the premise of the fix: safe_load silently discards the entry."""
    assert yaml.safe_load(DUPLICATE_CATEGORY)["bug fix"] == [
        {"title": "Second entry", "description": "second"},
    ]


def test_duplicate_key_within_entry_raises():
    """A key repeated inside a single change entry is rejected."""
    with pytest.raises(ValueError, match="Duplicate key 'title'"):
        load_yaml(
            "bug fix:\n- title: 'A'\n  description: 'a'\n  title: 'B'\n",
            "notes.yaml",
        )


def test_duplicate_key_under_files_raises():
    """A key repeated inside the files mapping is rejected."""
    with pytest.raises(ValueError, match="Duplicate key 'added'"):
        load_yaml(
            "bug fix:\n- files:\n    added:\n    - 'a.py'\n    added:\n    - 'b.py'\n",
            "notes.yaml",
        )


def test_repeated_keys_across_list_entries_are_not_duplicates():
    """
    Sibling entries each carrying a title are valid.

    This is brassy's normal shape, so a false positive here would reject
    every real multi-entry release note.
    """
    content = load_yaml(
        "bug fix:\n- title: 'A'\n  description: 'a'\n"
        "- title: 'B'\n  description: 'b'\n",
        "notes.yaml",
    )
    assert [entry["title"] for entry in content["bug fix"]] == ["A", "B"]


def test_merge_keys_still_resolve():
    """
    Merge keys must survive duplicate detection.

    The mapping has to be flattened before its keys are constructed; without
    that, "<<" reaches construct_object untagged and parsing blows up.
    """
    assert load_yaml("base: &b {a: 1}\nchild:\n  <<: *b\n  c: 2\n", "notes.yaml") == {
        "base": {"a": 1},
        "child": {"a": 1, "c": 2},
    }


def test_malformed_yaml_raises_value_error():
    """Syntax errors surface as ValueError, not a bare yaml.YAMLError."""
    with pytest.raises(ValueError, match=re.escape("Invalid YAML in notes.yaml")):
        load_yaml("bug fix:\n- title: 'unclosed\n", "notes.yaml")


@pytest.mark.parametrize(
    "input_file",
    [
        "barebones",
        "fully-featured",
        "mostly-featured",
        "real-world",
        "multi-entry",
        "to-prune",
    ],
)
def test_valid_fixtures_match_safe_load(input_file):
    """Every existing fixture loads, and loads identically to safe_load."""
    fixture = Path(__file__).resolve().parents[2] / "inputs" / f"{input_file}.yaml"
    with fixture.open() as f:
        expected = yaml.safe_load(f)
    with fixture.open() as f:
        assert load_yaml(f, str(fixture)) == expected

"""
Tests for brassy.templates.release_yaml_template.

This module provides fixtures and tests for
the brassy template that renders release YAML.
It covers data models such as Files, ChangeItem,
DateRange, RelatedIssue, and ReleaseNote, plus
integration with settings loading.
"""

import importlib
import sys
from datetime import date as Date  # noqa: N812
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

# Ensure we can import from src/
ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    src = parent / "src"
    if src.is_dir():
        sys.path.insert(0, str(src))
        break


@pytest.fixture
def settings_stub():
    """
    Return a minimal settings object used by tests.

    Includes a change_categories list for validation of
    category loading in the template module.
    """
    return SimpleNamespace(change_categories=["General", "Bug Fixes"])


@pytest.fixture
def module_under_test(monkeypatch, settings_stub):
    """
    Prepare the release_yaml_template module under test.

    Patches get_settings to return the settings_stub and
    ensures the template can be imported from brassy.utils.
    """
    # Import (or create) brassy.utils.settings_manager and patch get_settings
    sys.modules.pop("brassy.templates.release_yaml_template", None)

    try:
        settings_manager = importlib.import_module("brassy.utils.settings_manager")
    except ModuleNotFoundError:
        settings_manager = SimpleNamespace()
        sys.modules["brassy.utils.settings_manager"] = settings_manager

    monkeypatch.setattr(
        settings_manager,
        "get_settings",
        lambda _: settings_stub,
        raising=False,
    )

    module = importlib.import_module("brassy.templates.release_yaml_template")
    return module


def test_files_requires_at_least_one_field(module_under_test):
    """
    Ensure a Files instance requires at least one field.

    Validates that an empty instance raises a ValidationError
    with a message about missing deleted, moved, added,
    or modified values.
    """
    Files = module_under_test.Files  # noqa: N806

    with pytest.raises(ValidationError) as exc_info:
        Files()
    assert any(
        "At least one of deleted, moved, added, or modified must have a value"
        in err["msg"]
        for err in exc_info.value.errors()
    )


def test_files_accepts_when_field_is_provided(module_under_test):
    """
    Files accepts provided field values.

    When added is provided, other fields should default to
    empty lists.
    """
    Files = module_under_test.Files  # noqa: N806

    files = Files(added=["docs/readme.md"])
    assert files.added == ["docs/readme.md"]
    assert files.deleted == []
    assert files.moved == []
    assert files.modified == []


def test_related_issue_empty_repo_url_converted_to_none(module_under_test):
    """
    RelatedIssue repo_url empty string becomes None.

    Ensures normalization of an empty URL to None.
    """
    RelatedIssue = module_under_test.RelatedIssue  # noqa: N806

    related = RelatedIssue(number=42, repo_url="")
    assert related.repo_url is None


def test_date_range_parses_string_dates(module_under_test):
    """
    DateRange parses string dates to Date objects.

    start and finish strings are converted to Date instances.
    """
    DateRange = module_under_test.DateRange  # noqa: N806

    dr = DateRange(start="2023-07-15", finish="2023-07-20")
    assert dr.start == Date(2023, 7, 15)
    assert dr.finish == Date(2023, 7, 20)


def test_date_range_accepts_existing_date_objects(module_under_test):
    """
    DateRange accepts existing date objects.

    Start and finish passed as date objects are preserved.
    """
    DateRange = module_under_test.DateRange  # noqa: N806

    start = Date(2024, 1, 1)
    finish = Date(2024, 1, 10)
    dr = DateRange(start=start, finish=finish)
    assert dr.start == start
    assert dr.finish == finish


def test_date_range_handles_special_strings(module_under_test):
    """
    DateRange handles special strings.

    start="never" and finish="null" yield None values.
    """
    DateRange = module_under_test.DateRange  # noqa: N806

    dr = DateRange(start="never", finish="null")
    assert dr.start is None
    assert dr.finish is None


def test_date_range_invalid_string_raises(module_under_test):
    """
    DateRange raises on invalid parsing.

    Invalid date string should raise a ValidationError with
    'Could not parse date' in error messages.
    """
    DateRange = module_under_test.DateRange  # noqa: N806

    with pytest.raises(ValidationError) as exc_info:
        DateRange(start="not a real date")
    assert any("Could not parse date" in err["msg"] for err in exc_info.value.errors())


def test_date_range_unsupported_type_raises(module_under_test):
    """
    DateRange raises on unsupported input type.

    Passing a dict as start should trigger a validation error.
    """
    DateRange = module_under_test.DateRange  # noqa: N806

    with pytest.raises(ValidationError) as exc_info:
        DateRange(start={"unexpected": "type"})
    assert any(
        "Unsupported value type" in err["msg"] for err in exc_info.value.errors()
    )


def test_date_range_finish_before_start_raises(module_under_test):
    """
    Finish date before start raises.

    Ensures a ValidationError with proper message is produced.
    """
    DateRange = module_under_test.DateRange  # noqa: N806

    with pytest.raises(ValidationError) as exc_info:
        DateRange(start="2024-01-05", finish="2024-01-01")
    assert any(
        "Finish date cannot be before start date" in err["msg"]
        for err in exc_info.value.errors()
    )


def test_change_item_empty_strings_become_none(module_under_test):
    """
    Empty strings become None in ChangeItem.

    Title and description become None; files are preserved.
    """
    Files = module_under_test.Files  # noqa: N806
    ChangeItem = module_under_test.ChangeItem  # noqa: N806

    files = Files(added=["src/app.py"])
    item = ChangeItem(title="", description="", files=files)

    assert item.title is None
    assert item.description is None
    assert item.files.added == ["src/app.py"]


def test_release_note_accepts_change_items(module_under_test):
    """
    ReleaseNote accepts nested ChangeItem instances.

    Verifies that the structure preserves item titles.
    """
    Files = module_under_test.Files  # noqa: N806
    ChangeItem = module_under_test.ChangeItem  # noqa: N806
    ReleaseNote = module_under_test.ReleaseNote  # noqa: N806

    files = Files(added=["src/app.py"])
    item = ChangeItem(title="New feature", description="Added feature", files=files)
    note = ReleaseNote({"Features": [item]})

    assert note.root["Features"][0].title == "New feature"


def test_settings_categories_loaded(module_under_test, settings_stub):
    """
    Settings categories loaded from the stub.

    Asserts that module Settings equals the stub and
    categories reflect the stub's change_categories.
    """
    assert module_under_test.Settings is settings_stub
    assert module_under_test.categories == settings_stub.change_categories

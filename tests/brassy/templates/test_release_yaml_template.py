import importlib
import sys
from datetime import date as Date
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
    return SimpleNamespace(change_categories=["General", "Bug Fixes"])


@pytest.fixture
def module_under_test(monkeypatch, settings_stub):
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
    Files = module_under_test.Files

    with pytest.raises(ValidationError) as exc_info:
        Files()
    assert any(
        "At least one of deleted, moved, added, or modified must have a value"
        in err["msg"]
        for err in exc_info.value.errors()
    )


def test_files_accepts_when_field_is_provided(module_under_test):
    Files = module_under_test.Files

    files = Files(added=["docs/readme.md"])
    assert files.added == ["docs/readme.md"]
    assert files.deleted == []
    assert files.moved == []
    assert files.modified == []


def test_related_issue_empty_repo_url_converted_to_none(module_under_test):
    RelatedIssue = module_under_test.RelatedIssue

    related = RelatedIssue(number=42, repo_url="")
    assert related.repo_url is None


def test_date_range_parses_string_dates(module_under_test):
    DateRange = module_under_test.DateRange

    dr = DateRange(start="2023-07-15", finish="2023-07-20")
    assert dr.start == Date(2023, 7, 15)
    assert dr.finish == Date(2023, 7, 20)


def test_date_range_accepts_existing_date_objects(module_under_test):
    DateRange = module_under_test.DateRange

    start = Date(2024, 1, 1)
    finish = Date(2024, 1, 10)
    dr = DateRange(start=start, finish=finish)
    assert dr.start == start
    assert dr.finish == finish


def test_date_range_handles_special_strings(module_under_test):
    DateRange = module_under_test.DateRange

    dr = DateRange(start="never", finish="null")
    assert dr.start is None
    assert dr.finish is None


def test_date_range_invalid_string_raises(module_under_test):
    DateRange = module_under_test.DateRange

    with pytest.raises(ValidationError) as exc_info:
        DateRange(start="not a real date")
    assert any("Could not parse date" in err["msg"] for err in exc_info.value.errors())


def test_date_range_unsupported_type_raises(module_under_test):
    DateRange = module_under_test.DateRange

    with pytest.raises(ValidationError) as exc_info:
        DateRange(start={"unexpected": "type"})
    assert any(
        "Unsupported value type" in err["msg"] for err in exc_info.value.errors()
    )


def test_date_range_finish_before_start_raises(module_under_test):
    DateRange = module_under_test.DateRange

    with pytest.raises(ValidationError) as exc_info:
        DateRange(start="2024-01-05", finish="2024-01-01")
    assert any(
        "Finish date cannot be before start date" in err["msg"]
        for err in exc_info.value.errors()
    )


def test_change_item_empty_strings_become_none(module_under_test):
    Files = module_under_test.Files
    ChangeItem = module_under_test.ChangeItem

    files = Files(added=["src/app.py"])
    item = ChangeItem(title="", description="", files=files)

    assert item.title is None
    assert item.description is None
    assert item.files.added == ["src/app.py"]


def test_release_note_accepts_change_items(module_under_test):
    Files = module_under_test.Files
    ChangeItem = module_under_test.ChangeItem
    ReleaseNote = module_under_test.ReleaseNote

    files = Files(added=["src/app.py"])
    item = ChangeItem(title="New feature", description="Added feature", files=files)
    note = ReleaseNote({"Features": [item]})

    assert note.root["Features"][0].title == "New feature"


def test_settings_categories_loaded(module_under_test, settings_stub):
    assert module_under_test.Settings is settings_stub
    assert module_under_test.categories == settings_stub.change_categories

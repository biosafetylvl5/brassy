"""Release note YAML validation logic."""

from __future__ import annotations

from datetime import date as Date  # noqa N812
from typing import Any, Dict, List  # noqa: UP035

import dateparser
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    RootModel,
    field_validator,
    model_validator,
)

from brassy.utils.settings_manager import get_settings


class InvalidDateValueError(ValueError):
    """Error for invalid date strings."""

    def __init__(self, date_string: str) -> None:
        super().__init__(f"Invalid type for date field: {date_string}")


class Files(BaseModel):
    """Files model for validating files impacted in the changelog."""

    deleted: list[str] = []
    moved: list[str] = []
    added: list[str] = []
    modified: list[str] = []

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> Files:
        """Verify that at least one file is provided."""
        if not any(
            getattr(self, field) for field in ["deleted", "moved", "added", "modified"]
        ):
            raise ValueError(
                "At least one of deleted, moved, added, or modified must have a value",
            )
        return self


class RelatedInternalIssue(BaseModel):
    """Pydantic class for 'internal' or non-public related issue."""

    internal: str | None = Field(pattern=r"[A-Za-z]+#\d+ - .+", default=None)


class RelatedIssue(BaseModel):
    """Pydantic class for validating related issue (eg. GitHub issue)."""

    number: int | list[int] | None = None
    repo_url: HttpUrl | None = None

    @field_validator("repo_url", mode="before")
    @classmethod
    def convert_empty_to_none(cls, value: Any) -> Any | None:
        """Convert empty strings to None for URL validation."""
        if value == "":
            return None
        return value


class DateRange(BaseModel):
    """Date range model for pydantic validation."""

    start: Date | None = None
    finish: Date | None = None

    @field_validator("start", "finish", mode="before")
    @classmethod
    def parse_date(cls, value: Any) -> Date | None:
        """
        Parse and validate date values.

        Converts various date formats to a Date object, handling strings,
        Date objects, and None values.

        Parameters
        ----------
        value : Any
            Input to parse (Date, None, or string).

        Returns
        -------
        Date | None
            Parsed date or None for empty values.

        Raises
        ------
        InvalidDateValueError
            If the value cannot be parsed as a valid date
        """
        # Already correct type or None
        if value is None or isinstance(value, Date):
            return value

        # String values
        if isinstance(value, str):
            value = value.strip()
            if not value or value.lower() in ("never", "null"):
                return None

            parsed = dateparser.parse(
                value,
                settings={
                    "PARSERS": [
                        "timestamp",
                        "relative-time",
                        "absolute-time",
                        "no-spaces-time",
                    ],
                },
            )
            if parsed is None:
                raise InvalidDateValueError(f"Could not parse date: {value}")
            return parsed.date()
        raise InvalidDateValueError(f"Unsupported value type: {type(value)}")

    @model_validator(mode="after")
    def validate_date_range(self) -> DateRange:
        """Validate that finish date is not before start date if both are set."""
        if self.start and self.finish and self.finish < self.start:
            raise ValueError("Finish date cannot be before start date")
        return self


class ChangeItem(BaseModel):
    """A model representing a change "item", or an atomic change.

    This class provides a structured way to represent changes with associated metadata
    such as title, description, affected files, related issues, and date range.

    Attributes
    ----------
    model_config : ConfigDict
        Pydantic configuration. Forbids unknown fields so that misspelled keys
        are reported rather than silently ignored.
    title : str | None
        The title of the change item. Must be at least 1 character long if provided.
        Whitespace is stripped.
    description : str | None
        A detailed description of the change.
        Must be at least 1 character long if provided.
        Whitespace is stripped.
    files : Files
        The files affected by this change.
    related_issue : RelatedIssue | RelatedInternalIssue | None
        An issue related to this change. Aliased as "related-issue" in serialized form.
        Default is None.
    date : DateRange | None
        The date range associated with this change. Default is None.

    Notes
    -----
    Empty strings for 'title' and 'description' are automatically converted to None
    during validation.
    """

    model_config: ConfigDict = ConfigDict(extra="forbid")

    title: str | None = Field(min_length=1)
    description: str | None = Field(min_length=1)
    files: Files
    related_issue: RelatedIssue | RelatedInternalIssue | None = Field(
        alias="related-issue",
        default=None,
    )
    date: DateRange | None = None

    @field_validator("title", "description", mode="before")
    @classmethod
    def strip_whitespace_to_none(cls, value: Any) -> Any:
        """Strip whitespace from strings and convert empty results to None."""
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value

    @model_validator(mode="before")
    @classmethod
    def empty_str_to_none(cls, data: Any) -> Any:
        """
        Convert empty 'title'/'description' strings to None, mutating in place.

        The in-place mutation is load-bearing, not an accident: callers keep
        using the same parsed mapping after validation, and the blank-entry
        filter in ``read_yaml_files`` treats ``""`` (drop the entry) and
        ``None`` (keep it, render with defaults) differently.

        Parameters
        ----------
        data : Any
            The raw input for the change item, typically a mapping.

        Returns
        -------
        Any
            The input with empty 'title'/'description' strings converted to None.
        """
        if isinstance(data, dict):
            for key in ["title", "description"]:
                if data.get(key) == "":
                    data[key] = None
        return data


class ReleaseNote(RootModel[Dict[str, List[ChangeItem]]]):  # noqa: UP006
    """ReleaseNote is a root model for Release Notes.

    It contains a dictionary that maps category names to lists of ChangeItems.
    """

    pass


Settings = get_settings("brassy")

# List of categories stored in a variable
categories = Settings.change_categories

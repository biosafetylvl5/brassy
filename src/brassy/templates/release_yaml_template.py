from __future__ import annotations
from datetime import date as Date
from typing import List

import dateparser
from datetime import date as Date
from pydantic import (
  BaseModel,
  Field,
  HttpUrl,
  RootModel,
  field_validator,
  model_validator,
)

from brassy.utils.settings_manager import get_settings


class InvalidDateValue(ValueError):
  def __init__(self, date_string: str) -> None:
    super().__init__(f"Invalid type for date field: {date_string}")



class Files(BaseModel):
    deleted: List[str] = []
    moved: List[str] = []
    added: List[str] = []
    modified: List[str] = []

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        if not any(
            getattr(self, field) for field in ["deleted", "moved", "added", "modified"]
        ):
            raise ValueError(
                "At least one of deleted, moved, added, or modified must have a value",
            )
        return self


class RelatedInternalIssue(BaseModel):
    internal: str | None = Field(
        pattern=r"[A-Za-z]+#\d+ - .+", default=None)


class RelatedIssue(BaseModel):
    number: int | List[int] | None = None
    repo_url: HttpUrl | None = None

    @field_validator("repo_url", mode="before")
    @classmethod
    def convert_empty_to_none(cls, value):
        """Convert empty strings to None for URL validation."""
        if value == "":
            return None
        return value

class DateRange(BaseModel):
    start: Date | None = None
    finish: Date | None = None

    @field_validator("start", "finish", mode="before")
    @classmethod
    def parse_date(cls, value):
        """
        Parse and validate date values.

        Converts various date formats to a Date object, handling strings,
        Date objects, and None values.

        Args:
            value: Input to parse (Date, None, or string)

        Returns:
            Date or None: Parsed date or None for empty values

        Raises:
            InvalidDateValue: If the value cannot be parsed as a valid date
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
                        "no-spaces-time"
                    ]
                }
            )
            if parsed is None:
                raise InvalidDateValue(f"Could not parse date: {value}")
            return parsed.date()
        raise InvalidDateValue(f"Unsupported value type: {type(value)}")

    @model_validator(mode='after')
    def validate_date_range(self):
        """Validate that finish date is not before start date if both are set."""
        if self.start and self.finish and self.finish < self.start:
            raise ValueError("Finish date cannot be before start date")
        return self

class ChangeItem(BaseModel):
    """A model representing a change "item", or an atomic change.

    This class provides a structured way to represent changes with associated metadata
    such as title, description, affected files, related issues, and date range.

    Parameters
    ----------
    title : str or None, optional
        The title of the change item. Must be at least 1 character long if provided.
        Whitespace is stripped.
    description : str or None, optional
        A detailed description of the change.
        Must be at least 1 character long if provided.
        Whitespace is stripped.
    files : Files
        The files affected by this change.
    related_issue : RelatedIssue, RelatedInternalIssue, or None, optional
        An issue related to this change. Aliased as "related-issue" in serialized form.
        Default is None.
    date : DateRange or None, optional
        The date range associated with this change. Default is None.

    Notes
    -----
    Empty strings for 'title' and 'description' are automatically converted to None
    during validation.
    """

    title: str | None = Field(min_length=1, strip_whitespace=True)
    description: str | None = Field(min_length=1, strip_whitespace=True)
    files: Files
    related_issue: RelatedIssue | RelatedInternalIssue | None = Field(
        alias="related-issue", exclude_unset=True, default=None,
    )
    date: DateRange | None = None

    @model_validator(mode="before")
    def empty_str_to_none(self):
        """
        Convert empty strings to None for 'title' and 'description' attributes.

        This method checks if the 'title' or 'description' attributes of the object
        are empty strings and converts them to None if they are.

        Returns
        -------
        self : object
        Returns the instance itself to allow for method chaining.
        """
        for value in ["title", "description"]:
            if self[value] == "":
                self[value] = None
        return self


class ReleaseNote(RootModel[dict[str, List[ChangeItem]]]):
    """ReleaseNote is a root model for Release Notes.

    It contains a dictionary that maps category names to lists of ChangeItems.
    """

    pass


Settings = get_settings("brassy")

# List of categories stored in a variable
categories = Settings.change_categories

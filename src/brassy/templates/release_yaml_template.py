from datetime import date as Date

import dateparser
from pydantic import (
  BaseModel,
  Field,
  HttpUrl,
  RootModel,
  field_validator,
  model_validator,
  validator,
)

from brassy.utils.settings_manager import get_settings


class InvalidDateValue(ValueError):
  def __init__(self, date_string: str) -> None:
    super().__init__(f"Invalid type for date field: {date_string}")



class Files(BaseModel):
    deleted: list[str] = []
    moved: list[str] = []
    added: list[str] = []
    modified: list[str] = []

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
    number: int | list[int] | None = None
    repo_url: HttpUrl | None = None

    @field_validator("repo_url", mode="before")
    def blank_string(self, field):
        if self == "":
            return None
        return self


class DateRange(BaseModel):
    start: Date | None
    finish: Date | None

    @validator("start", "finish", pre=True, always=True)
    def parse_date(self, value):
        """
        Parse and validate date values for 'start' and 'finish' fields.

        This validator converts various date formats to a Date object. It handles
        strings, existing Date objects, and None values. String inputs are parsed
        using dateparser with support for timestamps, relative time, absolute time,
        and no-spaces time formats.

        Parameters
        ----------
        value : str, Date, None
            The value to parse. Can be:
            - A Date object (returned unchanged)
            - None (returned unchanged)
            - A string representing a date in various formats
            - Empty strings or "never"/"null" (converted to None)

        Returns
        -------
        Date or None
            The parsed date as a Date object, or None for empty/null values.

        Raises
        ------
        InvalidDateValue
            If the value cannot be parsed as a valid date or is of an unsupported type.

        Notes
        -----
        This validator enables "no-spaces-time" parsing which has a moderately high
        false positive rate.
        """
        if value is None or isinstance(value, Date):
            return value
        if isinstance(value, str):
            value = value.strip()
            if not value or value.lower() in ["never", "null"]:
                return None
            try:
                parsed = dateparser.parse(value,
                                          settings={"PARSERS":
                                                    ["timestamp",
                                                     "relative-time",
                                                     "absolute-time",
                                                     "no-spaces-time"]})
                if parsed is None:
                    raise InvalidDateValue(value)
                return parsed.date()
            except Exception as e:
                raise InvalidDateValue(value) from e
        raise InvalidDateValue(value)


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


class ReleaseNote(RootModel[dict[str, list[ChangeItem]]]):
    """ReleaseNote is a root model for Release Notes.

    It contains a dictionary that maps category names to lists of ChangeItems.
    """

    pass


Settings = get_settings("brassy")

# List of categories stored in a variable
categories = Settings.change_categories

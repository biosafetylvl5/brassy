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
    def blank_string(value, field):
        if value == "":
            return None
        return value


class DateRange(BaseModel):
    start: Date | None
    finish: Date | None

    @validator("start", "finish", pre=True, always=True)
    def parse_date(cls, value):
        if value is None or isinstance(value, Date):
            return value
        if isinstance(value, str):
            value = value.strip()
            if not value or value.lower() in ["never", "null"]:
                return None
            try:
                parsed = dateparser.parse(value, settings={"PARSERS": ["timestamp", "relative-time", "absolute-time", "no-spaces-time"]})
                if parsed is None:
                    raise ValueError(f"Unable to parse date string: {value}")
                return parsed.date()
            except Exception as e:
                raise ValueError(f"Invalid date format: {value}") from e
        raise ValueError(f"Invalid type for date field: {value}")


class ChangeItem(BaseModel):
    title: str | None = Field(min_length=1, strip_whitespace=True)
    description: str | None = Field(min_length=1, strip_whitespace=True)
    files: Files
    related_issue: RelatedIssue | RelatedInternalIssue | None = Field(
        alias="related-issue", exclude_unset=True, default=None,
    )
    date: DateRange | None = None

    @model_validator(mode="before")
    def empty_str_to_none(values):
        for value in ["title", "description"]:
            if values[value] == "":
                values[value] = None
        # if not values["title"] and not values["description"]:
        #    if not values == ReleaseNote():
        #        raise ValueError("Missing title and description")
        return values


class ReleaseNote(RootModel[dict[str, list[ChangeItem]]]):
    """
    ReleaseNote is a root model containing a dictionary that maps category names to lists of ChangeItems.
    """

    pass


Settings = get_settings("brassy")

# List of categories stored in a variable
categories = Settings.change_categories

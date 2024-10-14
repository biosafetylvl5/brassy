import pathlib
from typing import List, Optional, Dict, Union
from datetime import date as Date

import dateparser

from pydantic import (
    BaseModel,
    HttpUrl,
    ValidationError,
    model_validator,
    RootModel,
    Field,
    field_validator,
    validator,
)


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
                "At least one of deleted, moved, added, or modified must have a value"
            )
        return self


class RelatedInternalIssue(BaseModel):
    string: Optional[str] = Field(pattern=r"[A-Za-z]+#\d+ - .+", default=None)


class RelatedIssue(BaseModel):
    number: Optional[int] = None
    repo_url: Optional[HttpUrl] = None

    @field_validator("repo_url", mode="before")
    def blank_string(value, field):
        if value == "":
            return None
        return value


class DateRange(BaseModel):
    start: Optional[Date]
    finish: Optional[Date]

    @validator("start", "finish", pre=True, always=True)
    def parse_date(cls, value):
        if value is None or isinstance(value, Date):
            return value
        if isinstance(value, str):
            value = value.strip()
            if not value or value.lower() in ["never", "null"]:
                return None
            try:
                parsed = dateparser.parse(value)
                if parsed is None:
                    raise ValueError(f"Unable to parse date string: {value}")
                return parsed.date()
            except Exception as e:
                raise ValueError(f"Invalid date format: {value}") from e
        raise ValueError(f"Invalid type for date field: {value}")


class ChangeItem(BaseModel):
    title: str
    description: str
    files: Files
    related_issue: Optional[Union[RelatedIssue, RelatedInternalIssue]] = Field(
        alias="related-issue", exclude_unset=True, default=None
    )
    date: Optional[DateRange] = None


class ReleaseNote(RootModel[Dict[str, List[ChangeItem]]]):
    """
    ReleaseNote is a root model containing a dictionary that maps category names to lists of ChangeItems.
    """

    pass


# List of categories stored in a variable
categories = [
    "bug_fix",
    "enhancement",
    "deprecation",
    "removal",
    "performance",
    "documentation",
    "continuous_integration",
]

import pathlib
from typing import List, Optional, Dict
from datetime import date as Date

from pydantic import (
    BaseModel,
    HttpUrl,
    ValidationError,
    model_validator,
    RootModel,
    Field,
    field_validator,
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


class ChangeItem(BaseModel):
    title: str
    description: str
    files: Files
    related_issue: Optional[RelatedIssue] = Field(alias="related-issue")
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

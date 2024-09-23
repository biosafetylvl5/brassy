import pathlib
from typing import List

from pydantic import BaseModel


class Settings(BaseModel):
    use_color: bool = True
    default_yaml_path: pathlib.Path = "docs/source/releases/latest"
    change_categories: List[str] = [
        "bug fix",
        "enhancement",
        "deprecation",
        "removal",
        "performance",
        "documentation",
        "continuous integration",
    ]
    default_title: str = "NO TITLE"
    default_description: str = "NO DESCRIPTION"

    valid_fields: List[str] = ["title", "description", "files", "related-issue"]
    valid_changes: List[str] = ["deleted", "moved", "added", "modified"]

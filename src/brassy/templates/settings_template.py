import pathlib

from pydantic import BaseModel, Field
from typing import List
from __future__ import annotations


class ReleaseTemplate(BaseModel):
    release_template: List[dict[str, List[str]]] | None = Field(
        default=None, alias="release-template",
    )

    class Config:
        populate_by_name = True


# Example YAML representation (as a string for reference)
"""
release-template:
  - header:
    - {prefix_file}
  - title:
    - "Version {release_version} ({release_date})"
    - "**************************"
  - summary:
    - " * *{change_type}*: {title}"
  - entry:
    - "{change_type}"
    - "==========="
    - ""
    - "{title}"
    - "-------------------------"
    - ""
    - "{description}"
    - ""
    - "::"
    - ""
    - "     {file_change}: {file}"
  - footer:
    - {suffix_file}
"""

# Corrected instantiation of DefaultTemplate
DefaultTemplate = ReleaseTemplate(
    **{
        "release-template": [
            {"header": ["{prefix_file}", ""]},
            {
                "title": [
                    "",
                    "Version {release_version} ({release_date})",
                    "**************************",
                    "",
                ],
            },
            {"summary": [" * *{change_type}*: {title}"]},
            {
                "entry": [
                    "",
                    "{change_type}",
                    "===========",
                    "",
                    "{title}",
                    "-------------------------",
                    "",
                    "{description}",
                    "",
                    "::",
                    "",
                    "     {file_change}: {file}",
                ],
            },
            {"footer": ["", "{suffix_file}"]},
        ],
    },
)


class SettingsTemplate(BaseModel):
    use_color: bool = True
    default_yaml_path: pathlib.Path | None = None
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
    fail_on_empty_dir: bool = True
    description_populates_with_pipe: bool = False

    valid_fields: List[str] = ["title", "description", "files", "related-issue"]
    valid_changes: List[str] = ["deleted", "moved", "added", "modified"]
    enable_experimental_features: bool = False
    templates: ReleaseTemplate | None = DefaultTemplate

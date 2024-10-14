import pathlib
from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class ReleaseTemplate(BaseModel):
    release_template: List[Dict[str, List[str]]] = Field(
        default=None, alias="release-template"
    )

    class Config:
        populate_by_name = True


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

DefaultTemplate = ReleaseTemplate(
    **{
        "release-template": [
            {"header": ["{prefix_file}"]},
            {
                "title": [
                    "Version {release_version} ({release_date})",
                    "**************************",
                ]
            },
            {"summary": [" * *{change_type}*: {title}"]},
            {
                "entry": [
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
                ]
            },
            {"footer": ["{suffix_file}"]},
        ]
    }
)


class SettingsTemplate(BaseModel):
    use_color: bool = True
    default_yaml_path: Optional[pathlib.Path] = None
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
    enable_experimental_features: bool = False
    templates: List[ReleaseTemplate] = DefaultTemplate

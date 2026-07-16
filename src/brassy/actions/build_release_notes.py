"""Build release note output."""

# ruff: noqa: UP006, UP035, UP045

from __future__ import annotations

import sys
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import brassy
from brassy.brassy import Settings
from brassy.utils.messages import RichConsole as console  # noqa: N813


def get_header_footer(
    rich_open: Callable[..., Any],
    header_file: Optional[str] = None,
    footer_file: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """Read optional header and footer content.

    Parameters
    ----------
    rich_open : Callable[..., Any]
        Context manager factory for reading files.
    header_file : Optional[str]
        Path to header file.
    footer_file : Optional[str]
        Path to footer file.

    Returns
    -------
    Optional[str]
        Header content or None.
    Optional[str]
        Footer content or None.
    """

    def get_file(file: Optional[str]) -> Optional[str]:
        if not file:
            return None
        with rich_open(file, "r", description=f"Reading {file}") as open_file:
            return open_file.read()

    return get_file(header_file), get_file(footer_file)


def find_duplicate_titles(
    data: Dict[str, List[Dict[str, Any]]],
) -> bool:
    """Detect duplicate titles across changelog entries.

    Parameters
    ----------
    data : Dict[str, List[Dict[str, Any]]]
        Mapping of categories to lists of changelog entries.

    Returns
    -------
    bool
        True if any title occurs more than once.
    """
    titles = [entry["title"] for category in data for entry in data[category]]
    return len(set(titles)) != len(titles)


def format_files_changed_entry(
    detailed: bool,  # noqa: ARG001 TODO: Fix this unused arg
    entry: Dict[str, Any],
) -> str:
    """Format an RST block describing changed files for an entry.

    Parameters
    ----------
    detailed : bool
        Unused flag kept for compatibility.
    entry : Dict[str, Any]
        Changelog entry containing file changes.

    Returns
    -------
    str
        RST formatted file change listing.
    """
    files_changed = "::\n\n"
    for change_type in entry["files"]:
        files_changed += "".join(
            [
                f"    {change_type}: {file}\n"
                for file in filter(lambda x: x != "", entry["files"][change_type])
            ],
        )
    return files_changed


def generate_file_change_section_list_of_strings(
    entry: Dict[str, Any],
    line: str,
    category: str,
    title: str,
    description: str,
) -> List[str]:
    """Create file-specific section lines for a changelog entry.

    Parameters
    ----------
    entry : Dict[str, Any]
        Changelog entry with file change data.
    line : str
        Template string for the section line.
    category : str
        Entry category name.
    title : str
        Resolved entry title.
    description : str
        Resolved entry description.

    Returns
    -------
    List[str]
        Section lines formatted per file change.
    """
    lines = []
    for change_type in entry["files"]:
        if "{file}" in line:
            for file in filter(lambda x: x != "", entry["files"][change_type]):
                filename = file
                if "{" in filename:
                    filename = filename.replace("{","{{")
                if "}" in filename:
                    filename = filename.replace("}","}}")
                lines.append(
                    line.format(
                        change_type=category.capitalize(),
                        title=title,
                        description=description,
                        file_change=change_type,
                        file=filename,
                    ),
                )
        else:
            lines.append(
                line.format(
                    change_type=category.capitalize(),
                    title=title,
                    description=description,
                    file_change=change_type,
                ),
            )
    return lines


_ENTRY_BODY_KEYWORDS = ("{title}", "{description}", "{file_change}")
_ENTRY_KEYWORDS = (*_ENTRY_BODY_KEYWORDS, "{file}", "{change_type}")


def _split_template_lines(
    section_lines: List[str],
) -> Tuple[List[str], List[str]]:
    """Split template lines into category-level and entry-level parts.

    The split occurs at the first line that contains {title}, {description},
    or {file_change}. Lines before that point are category-level (rendered
    once per category); lines from that point onward are entry-level
    (rendered per entry).

    Parameters
    ----------
    section_lines : List[str]
        Template lines for a section.

    Returns
    -------
    List[str]
        Category-level template lines.
    List[str]
        Entry-level template lines.
    """
    for i, line in enumerate(section_lines):
        if any(kw in line for kw in _ENTRY_BODY_KEYWORDS):
            return section_lines[:i], section_lines[i:]
    return section_lines, []


def generate_section_string(  # noqa: PLR0913,PLR0912 TODO: Fix complexity of this function
    section_lines: List[str],
    changelog_entries: Dict[str, List[Dict[str, Any]]],
    release_date: str,
    version: str,
    footer: Optional[str],
    header: Optional[str],
) -> str:
    """Render a changelog section from templates and entries.

    Parameters
    ----------
    section_lines : List[str]
        Template lines for the section.
    changelog_entries : Dict[str, List[Dict[str, Any]]]
        Mapping of categories to changelog entries.
    release_date : str
        Release date string.
    version : str
        Release version string.
    footer : Optional[str]
        Footer content appended to templates.
    header : Optional[str]
        Header content prepended to templates.

    Returns
    -------
    str
        Rendered section content.
    """
    lines = []
    if any(keyword in line for keyword in _ENTRY_KEYWORDS for line in section_lines):
        category_lines, entry_lines = _split_template_lines(section_lines)
        for category, entries in changelog_entries.items():
            valid_entries = [e for e in entries if e["title"] or e["description"]]
            if not valid_entries:
                continue
            for line in category_lines:
                lines.append(line.format(change_type=category.capitalize()))
            for idx, entry in enumerate(valid_entries):
                if idx > 0 and category_lines:
                    lines.append("")
                if entry["title"]:
                    title = entry["title"].capitalize()
                else:
                    title = Settings.default_title
                if entry["description"]:
                    description = entry["description"]
                else:
                    description = Settings.default_description
                for line in entry_lines:
                    if "{file_change}" in line:
                        lines.extend(
                            generate_file_change_section_list_of_strings(
                                entry,
                                line,
                                category,
                                title,
                                description,
                            ),
                        )
                    else:
                        lines.append(
                            line.format(
                                change_type=category.capitalize(),
                                title=title,
                                description=description,
                            ),
                        )
    else:
        for line in section_lines:
            lines.append(line)
    for i, line in enumerate(lines):
        lines[i] = line.format(
            prefix_file=header,
            suffix_file=footer,
            release_version=version,
            release_date=release_date,
        )
    return "\n".join(lines)


def format_release_notes(
    data: Dict[str, List[Dict[str, Any]]],
    version: Optional[str],
    release_date: Optional[str] = None,
    header: Optional[str] = None,
    footer: Optional[str] = None,
) -> str:
    """Generate release notes content from parsed changelog data.

    Parameters
    ----------
    data : Dict[str, List[Dict[str, Any]]]
        Parsed changelog entries grouped by category.
    version : Optional[str]
        Release version string.
    release_date : Optional[str]
        Release date override in ISO format. Defaults to today's date.
    header : Optional[str]
        Optional header content.
    footer : Optional[str]
        Optional footer content.

    Returns
    -------
    str
        Release notes rendered in RST.
    """
    if release_date is None:
        release_date = datetime.now().strftime("%Y-%m-%d")

    header = header or ""
    footer = footer or ""

    release_template = Settings.templates.release_template
    formatted_string = ""
    for section in release_template:
        for _section_name, lines in section.items():
            formatted_string = (
                formatted_string
                + generate_section_string(
                    lines,
                    data,
                    release_date,
                    version,
                    footer,
                    header,
                )
                + "\n"
            )
    if Settings.default_title in formatted_string:
        console.print(
            "Warning: Build completed, but at least one title is missing.",
            style="yellow",
        )
    if Settings.default_description in formatted_string:
        console.print(
            "Warning: Build completed, but at least one description is missing.",
            style="yellow",
        )
    return formatted_string.strip()


def build_release_notes(  # noqa PLR0913
    input_files_or_folders: List[str],
    console: Any,
    rich_open: Callable[..., Any],
    version: Optional[str] = None,
    release_date: Optional[str] = None,
    header_file: Optional[str] = None,
    footer_file: Optional[str] = None,
    working_dir: str = ".",
) -> str:
    """Build release notes by reading YAML files and templates.

    Parameters
    ----------
    input_files_or_folders : List[str]
        CLI-supplied file or directory paths.
    console : Any
        Console for user feedback.
    rich_open : Callable[..., Any]
        Context manager factory for reading files.
    version : Optional[str]
        Release version string.
    release_date : Optional[str]
        Release date override in ISO format.
    header_file : Optional[str]
        Path to an optional header file.
    footer_file : Optional[str]
        Path to an optional footer file.
    working_dir : str
        Base directory for relative paths.

    Returns
    -------
    str
        Rendered release notes in RST.
    """
    yaml_files = brassy.utils.CLI.get_file_list_from_cli_input(
        input_files_or_folders,
        console,
        working_dir=working_dir,
    )
    try:
        data = brassy.utils.file_handler.read_yaml_files(yaml_files, rich_open)
    except (ValueError, TypeError) as e:
        console.print(f"[red]{e}")
        sys.exit(1)
    header, footer = get_header_footer(
        rich_open,
        header_file=header_file,
        footer_file=footer_file,
    )
    content = format_release_notes(
        data,
        version=version,
        release_date=release_date,
        header=header,
        footer=footer,
    )
    return content

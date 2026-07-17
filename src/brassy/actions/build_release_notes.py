"""Build release note output."""

from __future__ import annotations

import sys
from datetime import datetime
from typing import TYPE_CHECKING, Any

import brassy
from brassy.brassy import Settings

if TYPE_CHECKING:
    from collections.abc import Callable


def get_header_footer(
    rich_open: Callable[..., Any],
    header_file: str | None = None,
    footer_file: str | None = None,
) -> tuple[str | None, str | None]:
    """Read optional header and footer content.

    Parameters
    ----------
    rich_open : Callable[..., Any]
        Context manager factory for reading files.
    header_file : str | None
        Path to header file.
    footer_file : str | None
        Path to footer file.

    Returns
    -------
    str | None
        Header content or None.
    str | None
        Footer content or None.
    """

    def get_file(file: str | None) -> str | None:
        if not file:
            return None
        with rich_open(
            file,
            "r",
            encoding="utf-8",
            description=f"Reading {file}",
        ) as open_file:
            return open_file.read()

    return get_file(header_file), get_file(footer_file)


def find_duplicate_titles(
    data: dict[str, list[dict[str, Any]]],
) -> bool:
    """Detect duplicate titles across changelog entries.

    Parameters
    ----------
    data : dict[str, list[dict[str, Any]]]
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
    entry: dict[str, Any],
) -> str:
    """Format an RST block describing changed files for an entry.

    Parameters
    ----------
    detailed : bool
        Unused flag kept for compatibility.
    entry : dict[str, Any]
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
    entry: dict[str, Any],
    line: str,
    category: str,
    title: str,
    description: str,
) -> list[str]:
    """Create file-specific section lines for a changelog entry.

    Parameters
    ----------
    entry : dict[str, Any]
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
    list[str]
        Section lines formatted per file change.
    """
    lines = []
    issue_number, issue_url, issue_rst = _extract_issue_info(entry)
    title = _escape_braces(title)
    description = _escape_braces(description)
    issue_number = _escape_braces(issue_number)
    issue_url = _escape_braces(issue_url)
    issue_rst = _escape_braces(issue_rst)
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
                        issue_number=issue_number,
                        issue_url=issue_url,
                        issue=issue_rst,
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
                    issue_number=issue_number,
                    issue_url=issue_url,
                    issue=issue_rst,
                    file_change=change_type,
                ),
            )
    return lines


_ENTRY_BODY_KEYWORDS = (
    "{title}",
    "{description}",
    "{file_change}",
    "{issue}",
    "{issue_number}",
    "{issue_url}",
)
_ENTRY_KEYWORDS = (*_ENTRY_BODY_KEYWORDS, "{file}", "{change_type}")


def _extract_issue_info(entry: dict[str, Any]) -> tuple[str, str, str]:
    """Extract and format issue information from a changelog entry.

    Parameters
    ----------
    entry : dict[str, Any]
        Changelog entry dict possibly containing a "related-issue" key.

    Returns
    -------
    str
        Formatted issue number (e.g. "#1001") or empty string.
    str
        Issue URL string or empty string.
    str
        Fully formatted RST hyperlink (e.g. "`#1001 <url>`_")
        or empty string.
    """
    related = entry.get("related-issue") or {}
    internal = related.get("internal")
    if internal:
        return (internal, "", internal)

    number = related.get("number")
    url = str(related.get("repo_url") or "")
    if number is None or not url:
        return ("", "", "")

    formatted = (
        ", ".join(f"#{n}" for n in number)
        if isinstance(number, list)
        else f"#{number}"
    )
    return (formatted, url, f"`{formatted} <{url}>`_")


def _escape_braces(s: str) -> str:
    """Escape ``{`` and ``}`` so they pass through a format() call.

    Parameters
    ----------
    s : str
        A string that may contain curly braces.

    Returns
    -------
    str
        The string with ``{`` replaced by ``{{`` and ``}`` by ``}}``.
    """
    return s.replace("{", "{{").replace("}", "}}")


def _split_template_lines(
    section_lines: list[str],
) -> tuple[list[str], list[str]]:
    """Split template lines into category-level and entry-level parts.

    The split occurs at the first line that contains {title}, {description},
    or {file_change}. Lines before that point are category-level (rendered
    once per category); lines from that point onward are entry-level
    (rendered per entry).

    Parameters
    ----------
    section_lines : list[str]
        Template lines for a section.

    Returns
    -------
    list[str]
        Category-level template lines.
    list[str]
        Entry-level template lines.
    """
    for i, line in enumerate(section_lines):
        if any(kw in line for kw in _ENTRY_BODY_KEYWORDS):
            return section_lines[:i], section_lines[i:]
    return section_lines, []


def generate_section_string(  # noqa: PLR0913,PLR0912 TODO: Fix complexity of this function
    section_lines: list[str],
    changelog_entries: dict[str, list[dict[str, Any]]],
    release_date: str,
    version: str,
    footer: str | None,
    header: str | None,
) -> str:
    """Render a changelog section from templates and entries.

    Parameters
    ----------
    section_lines : list[str]
        Template lines for the section.
    changelog_entries : dict[str, list[dict[str, Any]]]
        Mapping of categories to changelog entries.
    release_date : str
        Release date string.
    version : str
        Release version string.
    footer : str | None
        Footer content appended to templates.
    header : str | None
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
                issue_number, issue_url, issue_rst = _extract_issue_info(entry)
                title = _escape_braces(title)
                description = _escape_braces(description)
                issue_number = _escape_braces(issue_number)
                issue_url = _escape_braces(issue_url)
                issue_rst = _escape_braces(issue_rst)
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
                                issue_number=issue_number,
                                issue_url=issue_url,
                                issue=issue_rst,
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
    data: dict[str, list[dict[str, Any]]],
    version: str | None,
    release_date: str | None = None,
    header: str | None = None,
    footer: str | None = None,
) -> str:
    """Generate release notes content from parsed changelog data.

    Parameters
    ----------
    data : dict[str, list[dict[str, Any]]]
        Parsed changelog entries grouped by category.
    version : str | None
        Release version string.
    release_date : str | None
        Release date override in ISO format. Defaults to today's date.
    header : str | None
        Optional header content.
    footer : str | None
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
    return formatted_string.strip()


def warn_on_missing_entry_fields(content: str, console: Any) -> None:
    """Warn when rendered notes still contain placeholder titles or descriptions.

    Parameters
    ----------
    content : str
        Rendered release notes to inspect.
    console : Any
        Console for user feedback.
    """
    if Settings.default_title in content:
        console.print(
            "Warning: Build completed, but at least one title is missing.",
            style="yellow",
        )
    if Settings.default_description in content:
        console.print(
            "Warning: Build completed, but at least one description is missing.",
            style="yellow",
        )


def build_release_notes(  # noqa: PLR0913
    input_files_or_folders: list[str],
    console: Any,
    rich_open: Callable[..., Any],
    version: str | None = None,
    release_date: str | None = None,
    header_file: str | None = None,
    footer_file: str | None = None,
    working_dir: str = ".",
    error_console: Any = None,
) -> str:
    """Build release notes by reading YAML files and templates.

    Parameters
    ----------
    input_files_or_folders : list[str]
        CLI-supplied file or directory paths.
    console : Any
        Console for status and warning output.
    rich_open : Callable[..., Any]
        Context manager factory for reading files.
    version : str | None
        Release version string.
    release_date : str | None
        Release date override in ISO format.
    header_file : str | None
        Path to an optional header file.
    footer_file : str | None
        Path to an optional footer file.
    working_dir : str
        Base directory for relative paths.
    error_console : Any
        Console for error output. Defaults to ``console`` when None.

    Returns
    -------
    str
        Rendered release notes in RST.
    """
    if error_console is None:
        error_console = console
    yaml_files = brassy.utils.CLI.get_file_list_from_cli_input(
        input_files_or_folders,
        console,
        working_dir=working_dir,
        error_console=error_console,
    )
    try:
        data = brassy.utils.file_handler.read_yaml_files(yaml_files, rich_open)
    except (ValueError, TypeError) as e:
        error_console.print(f"[red]{e}")
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
    warn_on_missing_entry_fields(content, console)
    return content

"""Build release note output."""

import sys
from datetime import datetime

import brassy
from brassy.brassy import Settings
from brassy.utils.messages import RichConsole as console  # noqa: N813


def get_header_footer(rich_open, header_file=None, footer_file=None):
    """Read optional header and footer content.

    Parameters
    ----------
    rich_open : Callable
        Context manager factory for reading files.
    header_file : str or None, optional
        Path to header file.
    footer_file : str or None, optional
        Path to footer file.

    Returns
    -------
    tuple of str or None
        Header and footer content or None when unavailable.
    """

    def get_file(file):
        if not file:
            return None
        with rich_open(file, "r", description=f"Reading {file}") as open_file:
            return open_file.read()

    return get_file(header_file), get_file(footer_file)


def find_duplicate_titles(data):
    """Detect duplicate titles across changelog entries.

    Parameters
    ----------
    data : dict
        Mapping of categories to lists of changelog entries.

    Returns
    -------
    bool
        True if any title occurs more than once.
    """
    titles = [entry["title"] for category in data for entry in data[category]]
    return len(set(titles)) != len(titles)


def format_files_changed_entry(detailed, entry): # noqa: ARG001 TODO: Fix this unused arg
    """Format an RST block describing changed files for an entry.

    Parameters
    ----------
    detailed : bool
        Unused flag kept for compatibility.
    entry : dict
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
    entry,
    line,
    category,
    title,
    description,
):
    """Create file-specific section lines for a changelog entry.

    Parameters
    ----------
    entry : dict
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
    list of str
        Section lines formatted per file change.
    """
    lines = []
    for change_type in entry["files"]:
        if "{file}" in line:
            for file in filter(lambda x: x != "", entry["files"][change_type]):
                lines.append(
                    line.format(
                        change_type=category.capitalize(),
                        title=title,
                        description=description,
                        file_change=change_type,
                        file=file,
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


def generate_section_string( # noqa: PLR0913,PLR0912 TODO: Fix complexity of this function
    section_lines,
    changelog_entries,
    release_date,
    version,
    footer,
    header,
):
    """Render a changelog section from templates and entries.

    Parameters
    ----------
    section_lines : list of str
        Template lines for the section.
    changelog_entries : dict
        Mapping of categories to changelog entries.
    release_date : str
        Release date string.
    version : str
        Release version string.
    footer : str or None
        Footer content appended to templates.
    header : str or None
        Header content prepended to templates.

    Returns
    -------
    str
        Rendered section content.
    """
    lines = []
    entry_keywords = [
        "{" + k + "}"
        for k in ["title", "description", "file_change", "file", "change_type"]
    ]
    if any(keyword in line for keyword in entry_keywords for line in section_lines):
        for category, entries in changelog_entries.items():
            for entry in entries:
                if not entry["title"] and not entry["description"]:
                    continue
                if entry["title"]:
                    title = entry["title"]
                    title = title.capitalize()
                else:
                    title = Settings.default_title
                if entry["description"]:
                    description = entry["description"]
                else:
                    description = Settings.default_description
                for line in section_lines:
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


def format_release_notes(data, version, release_date=None, header=None, footer=None):
    """Generate release notes content from parsed changelog data.

    Parameters
    ----------
    data : dict
        Parsed changelog entries grouped by category.
    version : str or None
        Release version string.
    release_date : str or None, optional
        Release date override in ISO format. Defaults to today's date.
    header : str or None, optional
        Optional header content.
    footer : str or None, optional
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


def build_release_notes( # noqa PLR0913
    input_files_or_folders,
    console,
    rich_open,
    version=None,
    release_date=None,
    header_file=None,
    footer_file=None,
    working_dir=".",
):
    """Build release notes by reading YAML files and templates.

    Parameters
    ----------
    input_files_or_folders : list of str
        CLI-supplied file or directory paths.
    console : Console
        Console for user feedback.
    rich_open : Callable
        Context manager factory for reading files.
    version : str or None, optional
        Release version string.
    release_date : str or None, optional
        Release date override in ISO format.
    header_file : str or None, optional
        Path to an optional header file.
    footer_file : str or None, optional
        Path to an optional footer file.
    working_dir : str, optional
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

from datetime import datetime

import brassy
from brassy.brassy import Settings


def get_header_footer(rich_open, header_file=None, footer_file=None):
    """
    Adds a header and/or footer to the given content.

    Args:
        content (str): The content to which the header and/or footer will be added.
        rich_open (function): A function used to open files.
        header_file (str, optional): The file containing the header content. Defaults to None.
        footer_file (str, optional): The file containing the footer content. Defaults to None.

    Returns:
        str: The content with the header and/or footer added.
    """

    def getFile(file):
        if not file:
            return None
        with rich_open(file, "r", description=f"Reading {file}") as file:
            return file.read()

    return getFile(header_file), getFile(footer_file)


def find_duplicate_titles(data):
    """
    Check if there are any duplicate titles in dictionaries of lists of dictionaries.

    Args:
        data (dict): A dictionary containing lists of dictionaries with items
         indexed by "title".

    Returns:
        bool: True if there are duplicate "title" values, False otherwise.
    """
    titles = [entry["title"] for category in data for entry in data[category]]
    return not len(set(titles)) == len(titles)


def format_files_changed_entry(detailed, entry):
    files_changed = "::\n\n"
    for change_type in entry["files"]:
        files_changed += "".join(
            [
                f"    {change_type}: {file}\n"
                for file in filter(lambda x: not x == "", entry["files"][change_type])
            ]
        )
    return files_changed


def generate_file_change_section_list_of_strings(
    entry, line, category, title, description
):
    lines = []
    for change_type in entry["files"]:
        if "{file}" in line:
            for file in filter(lambda x: not x == "", entry["files"][change_type]):
                lines.append(
                    line.format(
                        change_type=category.capitalize(),
                        title=title,
                        description=description,
                        file_change=change_type,
                        file=file,
                    )
                )
        else:
            lines.append(
                line.format(
                    change_type=category.capitalize(),
                    title=title,
                    description=description,
                    file_change=change_type,
                )
            )
    return lines


def generate_section_string(
    section_lines, changelog_entries, release_date, version, footer, header
):
    lines = []
    entry_keywords = [
        "{" + k + "}"
        for k in ["title", "description", "file_change", "file", "change_type"]
    ]
    if any([keyword in line for keyword in entry_keywords for line in section_lines]):
        for category, entries in changelog_entries.items():
            for entry in entries:
                for line in section_lines:
                    title = entry["title"].capitalize() or Settings.default_title
                    description = (
                        entry["description"].capitalize()
                        or Settings.default_description
                    )
                    if "{file_change}" in line:
                        lines.extend(
                            generate_file_change_section_list_of_strings(
                                entry, line, category, title, description
                            )
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
    """
    Format the parsed YAML data into release notes in .rst format.

    Parameters
    ----------
    data : dict
        Parsed content of YAML files.
    version : str, optional
        Version number of the release, by default '1.1'.
    release_date : str, optional
        Release date, by default None, which uses today's date.

    Returns
    -------
    str
        Formatted release notes in .rst format.
    """
    if release_date is None:
        release_date = datetime.now().strftime("%Y-%m-%d")

    header = header or ""
    footer = footer or ""

    release_template = Settings.templates.release_template
    formatted_string = ""
    for section in release_template:
        for section_name, lines in section.items():
            formatted_string = (
                formatted_string
                + generate_section_string(
                    lines, data, release_date, version, footer, header
                )
                + "\n"
            )
    return formatted_string.strip()


def build_release_notes(
    input_files_or_folders,
    console,
    rich_open,
    version=None,
    release_date=None,
    header_file=None,
    footer_file=None,
    working_dir=".",
):
    """
    Build release notes from YAML data.

    Parameters
    ----------
    data : dict
        Parsed content of YAML files.
    version : str, optional
        Version number of the release, by default '1.1'.
    release_date : str, optional
        Release date, by default None, which uses today's date.
    header_file : str, optional
        A header file to prepend to the release notes.
    footer_file : str, optional
        A footer file to suffix to the release notes.

    Returns
    -------
    str
        Formatted release notes in .rst format.
    """
    yaml_files = brassy.utils.CLI.get_file_list_from_cli_input(
        input_files_or_folders, console, working_dir=working_dir
    )
    try:
        data = brassy.utils.file_handler.read_yaml_files(yaml_files, rich_open)
    except (ValueError, TypeError) as e:
        console.print(f"[red]{e}")
        exit(1)
    header, footer = get_header_footer(
        rich_open, header_file=header_file, footer_file=footer_file
    )
    content = format_release_notes(
        data, version=version, release_date=release_date, header=header, footer=footer
    )
    return content

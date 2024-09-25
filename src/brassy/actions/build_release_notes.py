import datetime

import brassy

Settings = brassy.Settings


def add_header_footer(content, rich_open, header_file=None, footer_file=None):
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
        with rich_open(file, "r", description=f"Reading {file}") as file:
            return file.read()

    if header_file:
        content = getFile(header_file) + "\n" + content
    if footer_file:
        content = content + "\n" + getFile(footer_file)
    return content


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


def format_release_notes(data, version, release_date=None):
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

    header = f"Version {version} ({release_date})\n"
    header = header + ("*" * (len(header) - 1)) + ("\n" * 2)
    summary = ""
    detailed = ""

    for category, entries in data.items():
        detailed += f"{category.capitalize()}\n" + "=" * len(category) + "\n\n"
        for entry in entries:
            title = entry["title"]
            description = entry["description"]
            if title == "":
                title = Settings.default_title
            if description == "":
                description = Settings.default_description

            summary += f" * *{category.capitalize()}*: {title}\n"

            detailed += f"{title}\n" + "-" * len(title) + "\n\n"
            detailed += f"{description}\n\n"

            if "files" in entry:
                detailed += format_files_changed_entry(detailed, entry)
            detailed += "\n"

    return header + summary + "\n" + detailed[:-1]


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
    content = format_release_notes(data, version=version)
    content = add_header_footer(
        content, rich_open, header_file=header_file, footer_file=footer_file
    )
    return content

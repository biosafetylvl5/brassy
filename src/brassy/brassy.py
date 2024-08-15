"""
This module provides functionality to generate release notes from YAML files.
It reads YAML files, parses their content, and formats the parsed data into release notes in .rst format.
The release notes can be written to an output file.
"""

import argparse
import os
import rich.progress
import yaml
from datetime import datetime

import pygit2
from rich.console import Console
from rich_argparse import RichHelpFormatter

default_categories = [
    "bug fix",
    "enhancement",
    "deprecation",
    "removal",
    "performance",
    "documentation",
    "continuous integration",
]

default_title = "NO TITLE"
default_description = "NO DESCRIPTION"

valid_fields = ["title", "description", "files", "related-issue"]
valid_changes = ["deleted", "moved", "added", "modified"]


def get_rich_opener(no_format=False):
    """
    Returns the appropriate opener function for rich progress bar.

    Args:
        no_format (bool, optional): If True, returns the opener function without any formatting.
            If False, returns the opener function with formatting. Defaults to False.

    Returns:
        function: The opener function for rich progress bar.
    """
    if no_format:
        return rich.progress.Progress().open
    else:
        return rich.progress.open


def get_parser():
    """
    Returns an ArgumentParser object with predefined arguments for generating release notes from YAML files.

    Returns:
        argparse.ArgumentParser: The ArgumentParser object with predefined arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generate release notes from YAML files."
        + " Entries are sorted by order in yaml files, "
        + "and by order of yaml files provided via the command line.",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument(
        "-t",
        "--write-yaml-template",
        type=str,
        help="Write template YAML to provided file."
        + " If no value provided, use current git branch name as file name.",
        nargs="?",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-c",
        "--get-changed-files",
        type=str,
        help="Print git tracked file changes against main."
        + " If directory provided, use that directories checked-out branch.",
        nargs="?",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "input_files_or_folders",
        type=str,
        nargs="*",
        help="The folder(s) containing YAML files and/or YAML files. "
        + "Folders will be searched recursively.",
    )
    parser.add_argument(
        "-r",
        "--release-version",
        type=str,
        default="[UNKNOWN]",
        help="Version number of the release. Default is '[UNKNOWN]'.",
        required=False,
        dest="version",
    )
    parser.add_argument(
        "-d",
        "--release-date",
        type=str,
        help="Date of the release. Default is current system time.",
        required=False,
    )
    parser.add_argument(
        "-nc",
        "--no-color",
        action="store_true",
        default=False,
        help="Disable text formatting for CLI output.",
    )
    parser.add_argument(
        "-p",
        "--prefix-file",
        type=str,
        help="A header file to prepend to the release notes.",
    )
    parser.add_argument(
        "-s",
        "--suffix-file",
        type=str,
        help="A footer file to suffix to the release notes.",
    )
    parser.add_argument(
        "-o", "--output-file", type=str, help="The output file for release notes."
    )
    parser.add_argument(
        "--output-to-console",
        action="store_true",
        default=False,
        help="Write generated release notes to console.",
    )
    parser.add_argument(
        "-nr", "--no-rich", action="store_true", help="Disable rich text output"
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Only output errors")
    return parser


def parse_arguments():
    """
    Parse command line arguments for input folder and output file.

    Returns
    -------
    argparse.Namespace
        Parsed arguments containing input_folder and output_file.
    """
    parser = get_parser()
    return parser.parse_args(), parser


def exit_on_invalid_arguments(args, parser, console):
    """
    Validate the argparse arguments.

    This function validates the provided argparse arguments to ensure
    that the required input files/folders and output file are provided.
    If arguments are invalid, it prints an error message and exits the program.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed arguments.

    parser : argparse.ArgumentParser
        The ArgumentParser object used to parse the command-line arguments.
    """
    if bool(args.input_files_or_folders) or "get_changed_files" in args:
        return

    if "write_yaml_template" in args:
        return

    console.print("[bold red]Invalid arguments.\n")
    parser.print_help()
    exit(1)


def get_yaml_template_path(file_path_arg):
    """
    Returns the path of the YAML template file based on the given file path argument.

    Args:
        file_path_arg (str): The file path argument provided by the user.

    Returns:
        str: The path of the YAML template file.

    """
    if file_path_arg is None:
        filepath = os.getcwd()
        filename = f"{get_current_git_branch()}.yaml"
        return os.path.join(filepath, filename)
    if not (file_path_arg.endswith(".yaml") or file_path_arg.endswith(".yml")):
        return file_path_arg + ".yaml"
    return file_path_arg


def create_blank_template_yaml_file(file_path_arg, console):
    """
    Create a blank YAML file with default categories.

    Parameters
    ----------
    file_path : str
        Path to the output YAML file.
    """
    default_yaml = {
        category: [
            {
                "title": "",
                "description": "",
                "files": {change: [""] for change in valid_changes},
                "related-issue": {"number": 0, "repo_url": ""},
            }
        ]
        for category in default_categories
    }
    try:
        yaml_template_path = get_yaml_template_path(file_path_arg)
    except pygit2.GitError:
        console.print(
            "[bold red]Could not find a git repo. Please run in a "
            + "git repo or pass a file path for the yaml template "
            + "(eg '-t /path/to/file.yaml')."
        )
        exit(1)
    with open(yaml_template_path, "w") as file:
        yaml.dump(default_yaml, file)


def get_git_status(repo_path="."):
    """
    Retrieves the status of files in the given Git repository.

    Parameters:
    repo_path (str): The path to the Git repository. Defaults to the current directory.

    Returns:
    dict: A dictionary with keys 'added', 'modified', 'deleted', and 'renamed',
          each containing a list of file paths that match the respective status.
    """

    # Open the repository
    repo = pygit2.Repository(".")

    # Get the current branch reference
    current_branch = repo.head

    # Get the main branch reference
    main_branch = repo.branches["main"]

    # Get the commit objects
    current_commit = repo[current_branch.target]
    main_commit = repo[main_branch.target]

    # Get the diff between the current commit and the main branch commit
    diff = repo.diff(main_commit, current_commit)

    # Prepare dictionaries to store file statuses
    status = {
        "added": [],
        "modified": [],
        "deleted": [],
        "moved": [],
    }

    # Process the diff
    for delta in diff.deltas:
        if delta.status == pygit2.GIT_DELTA_ADDED:
            status["added"].append(delta.new_file.path)
        elif delta.status == pygit2.GIT_DELTA_MODIFIED:
            status["modified"].append(delta.new_file.path)
        elif delta.status == pygit2.GIT_DELTA_DELETED:
            status["deleted"].append(delta.old_file.path)
        elif delta.status == pygit2.GIT_DELTA_RENAMED:
            status["moved"].append((delta.old_file.path, delta.new_file.path))

    return {
        "added": status["added"],
        "modified": status["modified"],
        "deleted": status["deleted"],
        "moved": status["moved"],
    }


def print_out_git_changed_files(console, repo_path="."):
    status = get_git_status(repo_path=".")
    for entry in status:
        console.print(f"    {entry}:")
        for file in status[entry]:
            console.print(f"      - '{file}'")


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


def value_error_on_invalid_yaml(content, file_path):
    """
    Check if the YAML content follows the correct schema.

    Parameters
    ----------
    content : dict
        Parsed content of the YAML file.
    file_path : str
        Path to the YAML file.

    Raises
    ------
    ValueError
        If the YAML content does not follow the correct schema.
    """

    for category, entries in content.items():
        if not isinstance(entries, list):
            raise ValueError(
                f"Invalid YAML content in file {file_path}. "
                + f"Entries for category '{category}' must be a list."
            )

        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError(
                    f"Invalid YAML content in file {file_path}. "
                    + "Entry in category '{category}' must be a dictionary."
                )
            if not all([k in valid_fields for k in entry.keys()]):
                raise ValueError(
                    f"Invalid YAML content in file {file_path}. "
                    + f"Entry in category '{category}' must only have "
                    + ", ".join(valid_fields[:-1])
                    + f" and/or {valid_fields[-1]} "
                    + "keys."
                )
            if "files" in entry.keys():
                for change in entry["files"]:
                    if isinstance(change, dict):
                        raise TypeError(
                            f"Invalid YAML content in file {file_path}. "
                            + f"Entry in category '{category}' must only have "
                            + "strings representing the type of change."
                            + f" Got {change}."
                        )
                    if not change in valid_changes:
                        raise ValueError(
                            f"Invalid YAML content in file {file_path}. "
                            + f"Entry in category '{category}' must only have ("
                            + ", ".join(valid_changes)
                            + f") in 'files' key. Got {change}."
                        )
            else:
                raise ValueError(
                    f"Invalid YAML content in file {file_path}. "
                    + f"Entry in category '{category}' must have 'files' key."
                )


def read_yaml_files(input_files, rich_open):
    """
    Read and parse the given list of YAML files.

    Parameters
    ----------
    input_files : list
        List of paths to the YAML files.

    Returns
    -------
    dict
        Parsed content of all YAML files categorized by type of change.

    Examples
    --------
    >>> read_yaml_files(["file1.yaml", "file2.yaml"])
    {'bug-fix': [
        {'title': 'fixed explosions',
          'description': 'This fixed the explosion mechanism'},
        {'title': 'fixed cats not being cute',
          'description': 'This made the cats WAY cuter'}
        ]
    }
    """
    data = {}
    for file_path in input_files:
        with rich_open(file_path, "r", description=f"Reading {file_path}") as file:
            content = yaml.safe_load(file)
            value_error_on_invalid_yaml(content, file_path)
            for category, entries in content.items():
                entries = [
                    entry
                    for entry in entries
                    if not (entry["title"] == "" or entry["description"] == "")
                ]
                if category not in data and len(entries) > 0:
                    data[category] = []
                if len(entries) > 0:
                    data[category].extend(entries)
    return data


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
                title = default_title
            if description == "":
                description = default_description

            summary += f" * *{category.capitalize()}*: {title}\n"

            detailed += f"{title}\n" + "-" * len(title) + "\n\n"
            detailed += f"{description}\n\n"

            if "files" in entry:
                detailed += format_files_changed_entry(detailed, entry)
            detailed += "\n"

    return header + summary + "\n" + detailed[:-1]


def get_yaml_files_from_input(input_files_or_folders):
    """
    Get a list of YAML files from the given input files or folders.

    Parameters
    ----------
    input_files_or_folders : list
        List of paths to input files or folders.

    Returns
    -------
    list
        List of paths to YAML files.

    Raises
    ------
    ValueError
        If a file is not a YAML file or if no YAML files are found in a directory.
    """
    yaml_files = []
    for path in input_files_or_folders:
        if os.path.isfile(path):
            if not path.endswith(".yaml") or path.endswith(".yml"):
                raise ValueError(f"File {path} is not a YAML file.")
            yaml_files.append(path)
        elif os.path.isdir(path):
            dir_yaml_files = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".yaml") or file.endswith(".yml"):
                        dir_yaml_files.append(os.path.join(root, file))
            if len(dir_yaml_files) == 0:
                raise ValueError(f"No YAML files found in directory {path}.")
            yaml_files.extend(dir_yaml_files)
        else:
            raise FileNotFoundError(path)
    return yaml_files


def write_output_file(output_file, content):
    """
    Write the formatted release notes to the output file.

    Parameters
    ----------
    output_file : str
        Path to the output .rst file.
    content : str
        Formatted release notes.
    """
    with open(output_file, "w") as file:
        file.write(content)


def get_current_git_branch():
    """
    Get the current git branch name.

    Returns
    -------
    str
        The name of the current git branch.
    """
    repo = pygit2.Repository(".")
    return repo.head.shorthand


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


def build_release_notes(
    input_files_or_folders,
    console,
    rich_open,
    version=None,
    release_date=None,
    header_file=None,
    footer_file=None,
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
    try:
        yaml_files = get_yaml_files_from_input(input_files_or_folders)
    except FileNotFoundError as e:
        console.print(f"[red]Invalid file or directory: [bold]{e}[/]")
        exit(1)
    except ValueError as e:
        console.print(f"[red]{e}")
        exit(1)
    try:
        data = read_yaml_files(yaml_files, rich_open)
    except (ValueError, TypeError) as e:
        console.print(f"[red]{e}")
        exit(1)
    content = format_release_notes(data, version=version)
    content = add_header_footer(
        content, rich_open, header_file=header_file, footer_file=footer_file
    )
    return content


def setup_console(no_format=False, quiet=False):
    """
    Set up and return the console for printing messages.

    Args:
        no_format (bool, optional): Whether to disable formatting. Defaults to False.
        quiet (bool, optional): Whether to suppress console output. Defaults to False.

    Returns:
        Console: The configured rich console object.
    """
    console = Console(quiet=quiet, no_color=(no_format or quiet))
    return console


def run_from_CLI():
    """
    Main function to generate release notes from YAML files and write to an output file.
    """
    args, parser = parse_arguments()

    console = setup_console(args.no_rich, args.quiet)
    rich_open = get_rich_opener(args.no_rich or args.quiet)

    exit_on_invalid_arguments(args, parser, console)
    if "write_yaml_template" in args:
        create_blank_template_yaml_file(args.write_yaml_template, console)
    elif "get_changed_files" in args:
        print_out_git_changed_files(console, repo_path=args.get_changed_files)
    elif args.input_files_or_folders:
        content = build_release_notes(
            args.input_files_or_folders,
            console,
            rich_open,
            version=args.version,
            release_date=args.release_date,
            header_file=args.prefix_file,
            footer_file=args.suffix_file,
        )
        if args.output_file:
            write_output_file(args.output_file, content)
            if not args.quiet:
                console.print(f"[green]Wrote release notes to {args.output_file}")
        else:
            if not args.quiet:
                console.print(
                    f"[green]Release notes built successfully. No output file provided."
                )
        if args.output_to_console:
            console.print(content)

    else:
        parser.print_help()


if __name__ == "__main__":
    run_from_CLI()

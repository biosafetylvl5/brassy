"""Handle file system I/O."""

import sys
from pathlib import Path

import yaml
from pygit2 import GitError

from brassy.brassy import Settings
from brassy.templates.release_yaml_template import ReleaseNote
from brassy.utils import git_handler


def get_yaml_template_path(file_path_arg, working_dir=None):
    """
    Return path of the YAML template file based on the given file path argument.

    Args:
        file_path_arg (str): The file path argument provided by the user.

    Returns
    -------
        str: The path of the YAML template file.

    """
    if working_dir is None:
        working_dir = Path.getcwd()
    if file_path_arg is None:
        filename = Path(f"{git_handler.get_current_git_branch()}.yaml")
        return working_dir / filename
    else:
        file_path_arg = Path(file_path_arg)
    if ("/" in str(file_path_arg) or "\\" in str(file_path_arg)
        or Path(file_path_arg).is_file()):
        return file_path_arg
    return working_dir / file_path_arg


def create_blank_template_yaml_file(file_path_arg, console, working_dir="."):
    """
    Create a blank YAML template file with a predefined structure.

    This function generates a YAML file at the specified path with a default
    template. It handles special characters required for YAML compatibility and writes
    the file to disk.

    Parameters
    ----------
    file_path_arg : str
        The file path of the YAML template as passed via the CLI.
    console : rich.console.Console
        A Rich Console object used for displaying messages and errors to the user.
    working_dir : str, optional
        The working directory path. Defaults to the current directory ".".

    Raises
    ------
    SystemExit
        If a Git repo is not found in the current working directory and no file path
        is provided, the program exits with an error message.

    Notes
    -----
    This function performs a string replacement to insert a "|" due to an issue with
    YAML's handling of pipe symbols. For more details, see:
    https://github.com/yaml/pyyaml/pull/822
    """
    pipe_replace_string = "REPLACE_ME_WITH_PIPE"

    default_yaml = {
        category: [
            {
                "title": "",
                "description": (
                    pipe_replace_string
                    if Settings.description_populates_with_pipe
                    else ""
                ),
                "files": {change: [""] for change in Settings.valid_changes},
                "related-issue": {"number": None, "repo_url": ""},
                # in time, extract from the first and last commit
                "date": {"start": None, "finish": None},
            },
        ]
        for category in Settings.change_categories
    }
    try:
        yaml_template_path = get_yaml_template_path(file_path_arg, working_dir)
    except GitError:
        console.print(
            "[bold red]Could not find a git repo. Please run in a "
            + "git repo or pass a file path for the yaml template "
            + "(eg '-t /path/to/file.yaml').",
        )
        sys.exit(1)
    with Path(yaml_template_path).open("w") as file:
        yaml_text = yaml.safe_dump(
            default_yaml,
            sort_keys=False,
            default_flow_style=False,
        )
        if Settings.description_populates_with_pipe:
            yaml_text = yaml_text.replace(pipe_replace_string, "|\n    replace_me")
        file.write(yaml_text)


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
    if content is None:
        raise ValueError(f"No valid brassy-related YAML. Please populate {file_path}")

    ReleaseNote(**content)


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
                filtered_entries = [
                    entry
                    for entry in entries
                    if not (entry["title"] == "" or entry["description"] == "")
                ]
                if category not in data and len(filtered_entries) > 0:
                    data[category] = []
                if len(filtered_entries) > 0:
                    data[category].extend(filtered_entries)
    return data


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
    with Path(output_file).open("w") as file:
        file.write(content)

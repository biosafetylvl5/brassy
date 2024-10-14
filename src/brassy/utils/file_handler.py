import os
from pathlib import Path

import yaml
from pygit2 import GitError

import brassy.utils.git_handler as git_handler
from brassy.brassy import Settings


def get_yaml_template_path(file_path_arg, working_dir=os.getcwd()):
    """
    Returns the path of the YAML template file based on the given file path argument.

    Args:
        file_path_arg (str): The file path argument provided by the user.

    Returns:
        str: The path of the YAML template file.

    """
    if file_path_arg is None:
        filename = f"{git_handler.get_current_git_branch()}.yaml"
        return os.path.join(working_dir, filename)
    if "/" in file_path_arg or "\\" in file_path_arg or Path(file_path_arg).is_file():
        return file_path_arg
    return os.path.join(working_dir, file_path_arg)


def create_blank_template_yaml_file(file_path_arg, console, working_dir="."):
    """
    Creates a blank YAML template file with a predefined structure.

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
                "description": pipe_replace_string,
                "files": {change: [""] for change in Settings.valid_changes},
                "related-issue": {"number": None, "repo_url": ""},
                # in time, extract from the first and last commit
                "date": {"start": None, "finish": None},
            }
        ]
        for category in Settings.change_categories
    }
    try:
        yaml_template_path = get_yaml_template_path(file_path_arg, working_dir)
    except GitError:
        console.print(
            "[bold red]Could not find a git repo. Please run in a "
            + "git repo or pass a file path for the yaml template "
            + "(eg '-t /path/to/file.yaml')."
        )
        exit(1)
    with open(yaml_template_path, "w") as file:
        yaml_text = yaml.safe_dump(
            default_yaml, sort_keys=False, default_flow_style=False
        )
        yaml_text = yaml_text.replace(pipe_replace_string, "|")
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
    from brassy.templates.release_yaml_template import ReleaseNote

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

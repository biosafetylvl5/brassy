"""Provides functions for 'pruning' yaml of extra and empty fields."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

from brassy.utils.yaml_handler import load_yaml


def prune_empty(
    data: Any, prune_lists: bool = True, key: str = "",
) -> Any:
    """
    Recursively remove empty values from a nested dictionary or list.

    Parameters
    ----------
    data : Any
        The data structure to prune.
    prune_lists : bool
        Indicates whether to prune empty lists. Currently unused.
    key : str
        The key associated with the current data item, used for special cases.

    Returns
    -------
    Any
        The pruned data structure, or None if it is empty.

    Notes
    -----
    The function considers the following values as empty: `None`, empty strings,
    empty dictionaries, and empty lists. If a value is `0` and the key is
    `"number"`, it is also considered empty to address the related issues
    field which was previously set to 0 instead of null.

    Examples
    --------
    >>> data = {'a': None, 'b': '', 'c': {'d': [], 'e': 'value'}}
    >>> prune_empty(data)
    {'c': {'e': 'value'}}
    """
    nulls = (None, "", {}, [])
    if isinstance(data, dict):
        pruned = {k: prune_empty(v, key=k, prune_lists=prune_lists)
                  for k, v in data.items()}
        pruned = {k: v for k, v in pruned.items() if v not in nulls}
        return pruned if pruned else None
    elif isinstance(data, list) and prune_lists:
        pruned = [prune_empty(item, prune_lists=prune_lists) for item in data]
        pruned = [item for item in pruned if item not in nulls]
        return pruned if pruned else None
    elif data == 0 and key == "number":
        return None
    else:
        return data


def prune_yaml_file(
    yaml_file_path: str, console: Any,
) -> None:
    """
    Prune empty values from a YAML file and overwrite it with the pruned content.

    Parameters
    ----------
    yaml_file_path : str
        The file path to the YAML file to be pruned.
    console : Any
        An object used for printing messages to the console.

    Notes
    -----
    This function reads the YAML file, prunes empty values using `prune_empty`,
    and writes the pruned content back to the same file.

    Examples
    --------
    >>> prune_yaml_file('config.yaml', console)
    Pruned config.yaml
    """
    yaml_file_path = Path(yaml_file_path)
    with yaml_file_path.open("r+") as file:
        content = load_yaml(file, str(yaml_file_path))
        file.seek(0)
        file.write(
            yaml.dump(
                prune_empty(content, prune_lists=True),
                sort_keys=False,
                default_flow_style=False,
            ),
        )
        file.truncate()
    console.print(f"Pruned {yaml_file_path}")


def direct_pruning_of_files(
    input_files_or_folders: list[str],
    console: Any,
    working_dir: str,
    error_console: Any = None,
) -> None:
    """
    Prune empty values from YAML files specified by input paths.

    Parameters
    ----------
    input_files_or_folders : list[str]
        A list of file paths or directories containing YAML files to prune.
    console : Any
        An object used for printing status messages to the console.
    working_dir : str
        The working directory path.
    error_console : Any
        An object used for printing errors. Defaults to ``console`` when None.

    Notes
    -----
    This function collects YAML files from the specified input paths and
    prunes each file using `prune_yaml_file`.

    Examples
    --------
    >>> direct_pruning_of_files(['configs/'], console, '/home/user')
    Pruned configs/config1.yaml
    Pruned configs/config2.yaml
    """
    import brassy.utils.CLI  # noqa: PLC0415 # here to prevent circular import

    if error_console is None:
        error_console = console
    yaml_files = brassy.utils.CLI.get_file_list_from_cli_input(
        input_files_or_folders,
        console,
        working_dir=working_dir,
        error_console=error_console,
    )
    for yaml_file in yaml_files:
        try:
            prune_yaml_file(yaml_file, console)
        except ValueError as e:
            error_console.print(f"[red]{e}")
            sys.exit(1)

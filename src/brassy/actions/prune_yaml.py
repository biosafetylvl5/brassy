import yaml

import brassy
import brassy.utils
import brassy.utils.CLI
import brassy.utils.file_handler


def prune_empty(data, prune_lists=True, key=""):
    """
    Recursively remove empty values from a nested dictionary or list.

    Parameters
    ----------
    data : dict or list
        The data structure to prune.
    prune_lists : bool, optional
        Indicates whether to prune empty lists. Currently unused.
    key : str, optional
        The key associated with the current data item, used for special cases.

    Returns
    -------
    dict or list or None
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
        pruned = {k: prune_empty(v, key=k) for k, v in data.items()}
        pruned = {k: v for k, v in pruned.items() if v not in nulls}
        return pruned if pruned else None
    elif isinstance(data, list):
        pruned = [prune_empty(item) for item in data]
        pruned = [item for item in pruned if item not in nulls]
        return pruned if pruned else None
    elif data == 0 and key == "number":
        return None
    else:
        return data


def prune_yaml_file(yaml_file_path, console):
    """
    Prune empty values from a YAML file and overwrite it with the pruned content.

    Parameters
    ----------
    yaml_file_path : str
        The file path to the YAML file to be pruned.
    console : Console
        An object used for printing messages to the console.

    Returns
    -------
    None

    Notes
    -----
    This function reads the YAML file, prunes empty values using `prune_empty`,
    and writes the pruned content back to the same file.

    Examples
    --------
    >>> prune_yaml_file('config.yaml', console)
    Pruned config.yaml
    """
    with open(yaml_file_path, "r+") as file:
        content = yaml.safe_load(file)
        file.seek(0)
        file.write(
            yaml.dump(
                prune_empty(content, prune_lists=False),
                sort_keys=False,
                default_flow_style=False,
            )
        )
        file.truncate()
    console.print(f"Pruned {yaml_file_path}")


def direct_pruning_of_files(input_files_or_folders, console, working_dir):
    """
    Prune empty values from YAML files specified by input paths.

    Parameters
    ----------
    input_files_or_folders : list of str
        A list of file paths or directories containing YAML files to prune.
    console : Console
        An object used for printing messages to the console.
    working_dir : str
        The working directory path.

    Returns
    -------
    None

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
    yaml_files = brassy.utils.CLI.get_file_list_from_cli_input(
        input_files_or_folders, console, working_dir=working_dir
    )
    for yaml_file in yaml_files:
        prune_yaml_file(yaml_file, console)

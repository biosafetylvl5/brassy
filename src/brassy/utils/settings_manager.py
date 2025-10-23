"""Manages getting and setting settings."""

import os
from pathlib import Path

import platformdirs
import pygit2
import yaml
from pydantic import ValidationError

from brassy.templates.settings_template import SettingsTemplate


def get_git_repo_root(path="."):
    """
    Find the root directory of the Git repository for a path.

    Parameters
    ----------
    path : str, optional
        Path inside the repository. Defaults to ".".

    Returns
    -------
    Path
        Absolute path to the repository root (the dir that contains .git).
    """
    return (Path(pygit2.Repository(path).path) / "..").resolve()


def get_project_config_file_path(app_name):
    """
    Return the path to the project's configuration file.

    Parameters
    ----------
    app_name : str
        Name of the application.

    Returns
    -------
    Path
        Path to the project's configuration file. If the file does not
        exist locally, the path is resolved relative to the repository
        root when possible.
    """
    project_file = Path(f".{app_name}")
    if project_file.is_file():
        return project_file
    try:
        return get_git_repo_root() / project_file
    except pygit2.GitError:
        return project_file


def get_user_config_file_path(app_name):
    """
    Retrieve the user-specific configuration file path for the app.

    Parameters
    ----------
    app_name : str
        Name of the application.

    Returns
    -------
    Path
        Path to the user's configuration file.
    """
    return Path(platformdirs.user_config_dir(app_name)) / "user.config"


def get_site_config_file_path(app_name):
    """
    Retrieve the site-wide configuration file path for the app.

    Parameters
    ----------
    app_name : str
        Name of the application.

    Returns
    -------
    Path
        Path to the site's configuration file.
    """
    return Path(platformdirs.site_config_dir(app_name)) / "site.config"


def get_config_files(app_name):
    """
    Get configuration file paths in increasing precedence.

    Parameters
    ----------
    app_name : str
        Name of the application.

    Returns
    -------
    List[Path]
        List of configuration file paths. Site, user, then project.
    """
    config_files = []
    for f in [
        get_site_config_file_path,
        get_user_config_file_path,
        get_project_config_file_path,
    ]:
        path = f(app_name)
        config_files.append(path)
    return config_files


def create_config_file(config_file):
    """
    Create a configuration file with default settings.

    Parameters
    ----------
    config_file : Path
        Path where the configuration file will be created.
    """
    config_file = Path(config_file)
    default_settings = SettingsTemplate()
    config_dir = config_file.parent
    if config_dir:
        config_dir.makedirs(exist_ok=True, parents=True)
    with config_file.open("w") as f:
        yaml.dump(default_settings.model_dump(), f)


def read_config_file(config_file, create_file_if_not_exist=False):
    """
    Read and parse a YAML configuration file.

    Parameters
    ----------
    config_file : Path or str
        Path to the configuration file.
    create_file_if_not_exist : bool
        Creates file if it doesn't exist

    Returns
    -------
    dict
        Parsed configuration settings as a dictionary.
    """
    config_file = Path(config_file)
    try:
        with config_file.open() as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        if not create_file_if_not_exist:
            return SettingsTemplate().model_dump()
        else:
            create_config_file(config_file)
            return read_config_file(config_file)


def merge_and_validate_config_files(config_files):
    """
    Merge settings from multiple config files and validate them.

    Parameters
    ----------
    config_files : list of Path
        Paths to configuration files. Later files override earlier ones.

    Returns
    -------
    dict
        Merged and validated configuration settings.

    Raises
    ------
    ValidationError
        If any file's settings fail to validate against the
        SettingsTemplate model.
    """
    settings = {}
    for config_file in config_files:
        file_settings = read_config_file(config_file, create_file_if_not_exist=False)
        try:
            SettingsTemplate(**file_settings)
        except ValidationError as e:
            print(f"Failed to validate {config_file}")
            print(repr(e.errors()[0]))
            raise
        settings.update(file_settings)
    return settings


def get_settings_from_config_files(app_name):
    """
    Retrieve settings from configuration files without env overrides.

    Parameters
    ----------
    app_name : str
        Name of the application.

    Returns
    -------
    dict
        Configuration settings merged from files.
    """
    return merge_and_validate_config_files(get_config_files(app_name))


def override_dict_with_environmental_variables(input_dict):
    """Override dict values with case insensitive environment variables when available.

    Parameters
    ----------
    input_dict : dict
        Original settings dictionary.

    Returns
    -------
    dict
        Updated settings dictionary with environment variable overrides.
    """
    env_vars = dict(os.environ)
    lower_env_vars = {
        key.lower(): {"env_var": key, "value": value} for key, value in env_vars.items()
    }
    for key in input_dict:
        if key.lower() in lower_env_vars:
            override = lower_env_vars[key.lower()]
            input_dict[key] = override["value"]
    return input_dict


def get_settings(app_name):
    """
    Return final application settings with file and env overrides.

    Parameters
    ----------
    app_name : str
        Name of the application.

    Returns
    -------
    SettingsTemplate
        An instance containing the merged configuration.

    Raises
    ------
    ValidationError
        If the final settings fail to validate against the model.
    """
    file_settings = override_dict_with_environmental_variables(
        get_settings_from_config_files(app_name),
    )
    settings = SettingsTemplate(**file_settings)
    return settings

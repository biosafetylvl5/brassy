"""Manages getting and setting settings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import platformdirs
import pygit2
import yaml
from pydantic import ValidationError

from brassy.templates.settings_template import SettingsTemplate
from brassy.utils.yaml_handler import load_yaml


def get_git_repo_root(path: str = ".") -> Path:
    """
    Find the root directory of the Git repository for a path.

    Parameters
    ----------
    path : str
        Path inside the repository. Defaults to ".".

    Returns
    -------
    Path
        Absolute path to the repository root (the dir that contains .git).
    """
    return (Path(pygit2.Repository(path).path) / "..").resolve()


def get_project_config_file_path(app_name: str) -> Path:
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


def get_user_config_file_path(app_name: str) -> Path:
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


def get_site_config_file_path(app_name: str) -> Path:
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


def get_config_files(app_name: str) -> list[Path]:
    """
    Get configuration file paths in increasing precedence.

    Parameters
    ----------
    app_name : str
        Name of the application.

    Returns
    -------
    list[Path]
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


def create_config_file(config_file: Path) -> None:
    """
    Create a configuration file with default settings.

    Parameters
    ----------
    config_file : Path
        Path where the configuration file will be created.
    """
    config_file = Path(config_file)
    default_settings = SettingsTemplate()
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with config_file.open("w") as f:
        yaml.dump(default_settings.model_dump(), f)


def read_config_file(
    config_file: Path | str,
    create_file_if_not_exist: bool = False,
) -> dict[str, Any]:
    """
    Read and parse a YAML configuration file.

    Parameters
    ----------
    config_file : Path | str
        Path to the configuration file.
    create_file_if_not_exist : bool
        Creates file if it doesn't exist

    Returns
    -------
    dict[str, Any]
        Parsed configuration settings as a dictionary. A missing or empty
        file contributes an empty dictionary.

    Raises
    ------
    ValueError
        If the file exists but does not contain a YAML mapping.
    """
    config_file = Path(config_file)
    try:
        with config_file.open() as f:
            content = load_yaml(f, str(config_file))
    except FileNotFoundError:
        if not create_file_if_not_exist:
            return {}
        create_config_file(config_file)
        return read_config_file(config_file)
    if content is None:
        return {}
    if not isinstance(content, dict):
        # ValueError, not TypeError: malformed user input raises ValueError
        # everywhere else in brassy (see yaml_handler.load_yaml).
        raise ValueError(  # noqa: TRY004
            f"Settings file {config_file} must contain a YAML mapping of settings.",
        )
    return content


def merge_and_validate_config_files(
    config_files: list[Path],
) -> dict[str, Any]:
    """
    Merge settings from multiple config files and validate them.

    Parameters
    ----------
    config_files : list[Path]
        Paths to configuration files. Later files override earlier ones.

    Returns
    -------
    dict[str, Any]
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


def get_settings_from_config_files(app_name: str) -> dict[str, Any]:
    """
    Retrieve settings from configuration files without env overrides.

    Parameters
    ----------
    app_name : str
        Name of the application.

    Returns
    -------
    dict[str, Any]
        Configuration settings merged from files.
    """
    return merge_and_validate_config_files(get_config_files(app_name))


def override_dict_with_environmental_variables(
    input_dict: dict[str, Any],
) -> dict[str, Any]:
    """Override dict values with case insensitive environment variables when available.

    Every field of :class:`SettingsTemplate` is considered, so an environment
    variable applies even when the setting is absent from the input dictionary
    (for example when no configuration file exists).

    Parameters
    ----------
    input_dict : dict[str, Any]
        Original settings dictionary.

    Returns
    -------
    dict[str, Any]
        Updated settings dictionary with environment variable overrides.
    """
    lower_env_vars = {key.lower(): value for key, value in os.environ.items()}
    for field_name in SettingsTemplate.model_fields:
        prefixed_key = "brassy_" + field_name.lower()
        if prefixed_key in lower_env_vars:
            input_dict[field_name] = lower_env_vars[prefixed_key]
    return input_dict


def get_settings(app_name: str) -> SettingsTemplate:
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
    """
    file_settings = override_dict_with_environmental_variables(
        get_settings_from_config_files(app_name),
    )
    settings = SettingsTemplate(**file_settings)
    return settings

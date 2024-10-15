import os

from pydantic import ValidationError
import platformdirs
import pygit2
import yaml

from brassy.templates.settings_template import SettingsTemplate


def get_git_repo_root(path="."):
    """
    Get the root directory of the Git repository containing the given path.

    Parameters
    ----------
    path : str, optional
        A path within the Git repository. Defaults to the current directory.

    Returns
    -------
    str
        Absolute path to the root of the Git repository. This is usually the
        path containing the .git folder.
    """
    return os.path.abspath(os.path.join(pygit2.Repository(path).path, ".."))


def get_project_config_file_path(app_name):
    """
    Retrieve the project-specific configuration file path for the application.

    Parameters
    ----------
    app_name : str
        Name of the application.

    Returns
    -------
    str
        Path to the project's configuration file.
    """
    project_file = f".{app_name}"
    if os.path.isfile(project_file):
        return project_file
    try:
        return os.path.join(get_git_repo_root(), project_file)
    except pygit2.GitError:
        return project_file


def get_user_config_file_path(app_name):
    """
    Retrieve the user-specific configuration file path for the application.

    Parameters
    ----------
    app_name : str
        Name of the application.

    Returns
    -------
    str
        Path to the user's configuration file.
    """
    return os.path.join(platformdirs.user_config_dir(app_name), "user.config")


def get_site_config_file_path(app_name):
    """
    Retrieve the site-specific configuration file path for the application.

    Parameters
    ----------
    app_name : str
        Name of the application.

    Returns
    -------
    str
        Path to the site's configuration file.
    """
    return os.path.join(platformdirs.site_config_dir(app_name), "site.config")


def get_config_files(app_name):
    """
    Get a list of configuration file paths in order of increasing precedence.

    Parameters
    ----------
    app_name : str
        Name of the application.

    Returns
    -------
    list of str
        List of configuration file paths.
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
    config_file : str
        Path where the configuration file will be created.
    """
    default_settings = SettingsTemplate()
    config_dir = os.path.dirname(config_file)
    if config_dir:
        os.makedirs(config_dir, exist_ok=True)
    with open(config_file, "wt") as f:
        yaml.dump(default_settings.dict(), f)


def read_config_file(config_file, create_file_if_not_exist=False):
    """
    Read and parse a YAML configuration file.

    Parameters
    ----------
    config_file : str
        Path to the configuration file.
    create_file_if_not_exist : bool
        Creates file if it doesn't exist

    Returns
    -------
    dict
        Parsed configuration settings.
    """
    try:
        with open(config_file, "rt") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        if not create_file_if_not_exist:
            return SettingsTemplate().dict()
        else:
            create_config_file(config_file)
            return read_config_file(config_file)


def merge_and_validate_config_files(config_files):
    """
    Merge settings from multiple configuration files and validate them.

    Parameters
    ----------
    config_files : list of str
        List of configuration file paths. The order of the files matters.
        Each file overwrites the values of the previous.

    Returns
    -------
    dict
        Merged and validated configuration settings.

    Raises
    ------
    ValidationError
        If any of the settings do not conform to the `Settings` model.
    """
    settings = {}
    for config_file in config_files:
        file_settings = read_config_file(config_file, create_file_if_not_exist=False)
        try:
            SettingsTemplate(**file_settings)
        except ValidationError as e:
            print(f"Failed to validate {config_file}")
            print(repr(e.errors()[0]))
            raise e
        settings.update(file_settings)
    return settings


def get_settings_from_config_files(app_name):
    """
    Retrieve settings from configuration files without environment overrides.

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
    """
    Override dict values with case insensitive environment variables when available.


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
    for key in input_dict.keys():
        if key.lower() in lower_env_vars:
            override = lower_env_vars[key.lower()]
            # print(
            #    f"Overriding value {key} with environmental "
            #    f"variable {override['env_var']} "
            #    f"with value {override['value']}"
            # )
            input_dict[key] = override["value"]
    return input_dict


def get_settings(app_name):
    """
    Return application settings from config files and environment variables.

    Parameters
    ----------
    app_name : str
        Name of the application.

    Returns
    -------
    Settings
        An instance of the `Settings` model with all configurations applied.

    Raises
    ------
    ValidationError
        If the final settings do not conform to the `Settings` model.
    """
    file_settings = override_dict_with_environmental_variables(
        get_settings_from_config_files(app_name)
    )
    Settings = SettingsTemplate(**file_settings)
    return Settings

import os

from pydantic import ValidationError
import platformdirs
import pygit2
import yaml

from brassy.settings_template import Settings


def get_git_repo_root(path="."):
    return os.path.abspath(os.path.join(pygit2.Repository(path).path, ".."))


def get_project_config_file_path(app_name):
    project_file = f".{app_name}"
    if os.path.isfile(project_file):
        return project_file
    try:
        return os.path.join(get_git_repo_root(), project_file)
    except pygit2.GitError:
        return project_file


def get_user_config_file_path(app_name):
    return os.path.join(platformdirs.user_config_dir(app_name), f"user.config")


def get_site_config_file_path(app_name):
    return os.path.join(platformdirs.site_config_dir(app_name), f"site.config")


def get_config_files(app_name):
    # Returns a list of configuration file paths in order of increasing precedence.
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
    default_settings = Settings()
    config_dir = os.path.dirname(config_file)
    if config_dir:
        os.makedirs(config_dir, exist_ok=True)
    with open(config_file, "wt") as f:
        yaml.dump(default_settings.dict(), f)


def read_config_file(config_file):
    try:
        with open(config_file, "rt") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        create_config_file(config_file)
        return read_config_file(config_file)


def merge_and_validate_config_files(config_files):
    settings = {}
    for config_file in config_files:
        file_settings = read_config_file(config_file)
        try:
            Settings(**file_settings)
        except ValidationError as e:
            print(f"Failed to validate {config_file}")
            print(repr(e.errors()[0]))
            raise e
        settings.update(file_settings)
    return settings


def get_raw_config_file_settings(app_name):
    return merge_and_validate_config_files(get_config_files(app_name))


def override_dict_with_environmental_variables(input_dict):
    env_vars = dict(os.environ)
    lower_env_vars = {
        entry.lower(): {"env_var": entry, "value": value}
        for entry, value in env_vars.items()
    }
    for key in input_dict.keys():
        if key.lower() in lower_env_vars:
            override = lower_env_vars[key.lower()]
            print(
                f"Overriding value {key} with environmental"
                + f" variable {override['env_var']}"
                + f" with value {override['value']}"
            )
            input_dict[key] = override["value"]
    return input_dict


def get_settings(app_name):
    file_settings = override_dict_with_environmental_variables(
        get_raw_config_file_settings(app_name)
    )
    return Settings(**file_settings)

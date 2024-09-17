import os

import pydantic
import platformdirs
import pygit2
import yaml

app_name = "brassy"


def get_git_repo_root(path="."):
    return pygit2.Repository(path).path


def get_project_config_file_path(app_name):
    if os.path.isfile(f".{app_name}"):
        return f".{app_name}"
    git_root_config = os.path.join(get_git_repo_root(), f".{app_name}")
    if os.path.isfile(git_root_config):
        return git_root_config


def get_user_config_file_path(app_name):
    return os.path.join(
        platformdirs.user_config_dir(app_name), f"{app_name}.user.config"
    )


def get_site_config_file_path(app_name):
    return os.path.join(
        platformdirs.user_config_dir(app_name), f"{app_name}.site.config"
    )


def get_config_files():
    # returns a list of config files, they are returned in order of dominance
    config_files = []
    for f in [
        get_site_config_file_path,
        get_user_config_file_path,
        get_project_config_file_path,
    ]:
        path = f(app_name)
        if os.path.isfile(path):
            config_files.append(path)
    platformdirs.user_config_dir(app_name)
    return config_files


def merge_config_files(config_files):
    settings = {}
    for config_file in config_files:
        try:
            file_settings = yaml.safe_load(config_file)
        except FileNotFoundError:
            continue
        settings.update(file_settings)
    return settings


def get_raw_config_file_settings():
    return merge_config_files(get_config_files())


def override_dict_with_environmental_variables(input_dict):
    env_vars = dict(os.environ)
    lower_env_vars = {
        entry.lower: {"env_var": entry, "value": value} for entry, value in env_vars
    }
    for key in input_dict.keys():
        if key.lower() in lower_env_vars:
            print(
                f"Overriding value {key} with environmental"
                + f" variable {lower_env_vars['env_var']}"
            )
            input_dict[key] = lower_env_vars[key]["value"]


override_dict_with_environmental_variables(get_raw_config_file_settings())

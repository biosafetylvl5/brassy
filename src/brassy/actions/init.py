import brassy


def init():
    """
    Initialize configuration files for the application.

    This function creates site and user configuration files, and optionally
    a project configuration file based on user input.

    Returns
    -------
    None

    Examples
    --------
    >>> init()
    Do you want to create a project config file? [y/N]: y
    """
    conf_files = [
        brassy.utils.settings_manager.get_site_config_file_path("brassy"),
        brassy.utils.settings_manager.get_user_config_file_path("brassy"),
    ]
    for conf_file in conf_files:
        brassy.utils.settings_manager.create_config_file(conf_file)
    if brassy.utils.messages.boolean_prompt(
        "Do you want to create a project config file?"
    ):
        brassy.utils.settings_manager.create_config_file(
            brassy.utils.settings_manager.get_project_config_file_path("brassy")
        )

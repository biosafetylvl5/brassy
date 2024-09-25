def get_rich_opener(no_format=False):
    """
    Returns the appropriate opener function for rich progress bar.

    Args:
        no_format (bool, optional): If True, returns the opener function without any formatting.
            If False, returns the opener function with formatting. Defaults to False.

    Returns:
        function: The opener function for rich progress bar.
    """
    if no_format:
        return rich.progress.Progress().open
    else:
        return rich.progress.open


def setup_console(no_format=False, quiet=False):
    """
    Set up and return the console for printing messages.

    Args:
        no_format (bool, optional): Whether to disable formatting. Defaults to False.
        quiet (bool, optional): Whether to suppress console output. Defaults to False.

    Returns:
        Console: The configured rich console object.
    """
    if not no_format:
        install_rich_tracebacks()
    console = Console(quiet=quiet, no_color=(no_format or quiet))
    return console

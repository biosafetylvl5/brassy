import logging
import rich
from rich.logging import RichHandler
from rich.console import Console as rich_console
from rich.prompt import Confirm
from rich.traceback import install as install_rich_tracebacks

logging.captureWarnings(True)


def init_logger(use_rich):
    """
    Initialize and configure the logger.

    Parameters
    ----------
    use_rich : bool
        If True, sets up rich logging else use standard stream logging

    Returns
    -------
    logger : logging.Logger
        The configured logger instance
    """
    logger = logging.getLogger("build_docs")
    if use_rich:
        install_rich_tracebacks()
        logging_handlers = [RichHandler(rich_tracebacks=True)]
    else:
        logging_handlers = [logging.StreamHandler()]

    logging.basicConfig(level=logging.DEBUG, datefmt="[%X]", handlers=logging_handlers)
    logger.debug("Program initialized")
    return logger


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
    console = rich_console(quiet=quiet, no_color=(no_format or quiet))
    return console


def get_boolean_prompt_function(format=True):
    if format:
        return Confirm.ask
    else:

        def bool_prompt(question):
            answer = input(question).lower()
            if answer in ["yes", "y", "ye"]:
                return True
            elif answer in ["no", "n", ""]:
                return False
            else:
                print("Please respond with 'yes' or 'no'.")
                return bool_prompt(question)

        return bool_prompt


def setup_messages(format, quiet):
    global open
    global boolean_prompt
    global RichConsole
    global print
    open = get_rich_opener(no_format=not format)
    RichConsole = setup_console(no_format=not format, quiet=quiet)
    print = RichConsole.print if format else print
    boolean_prompt = get_boolean_prompt_function(format=format)


open = get_rich_opener()
RichConsole = setup_console()
print = RichConsole.print
boolean_prompt = get_boolean_prompt_function()

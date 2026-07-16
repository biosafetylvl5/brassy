"""Handle outputs/inputs to the CLI."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

import rich
import rich.progress
from rich.console import Console as rich_console  # noqa: N813
from rich.logging import RichHandler
from rich.prompt import Confirm
from rich.traceback import install as install_rich_tracebacks

logging.captureWarnings(True)


def init_logger(use_rich: bool) -> logging.Logger:
    """
    Initialize and configure the logger.

    Parameters
    ----------
    use_rich : bool
        If True, sets up rich logging else use standard stream logging.

    Returns
    -------
    logging.Logger
        The configured logger instance.
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


def get_rich_opener(no_format: bool = False) -> Callable[..., Any]:
    """
    Return opener function with or without a rich progress bar.

    Parameters
    ----------
    no_format : bool
        If True, returns the opener function without any formatting.
        If False, returns the opener function with formatting. Defaults to False.

    Returns
    -------
    Callable[..., Any]
        The opener function for rich progress bar.
    """
    if no_format:
        return rich.progress.Progress().open
    else:
        return rich.progress.open


def setup_console(no_format: bool = False, quiet: bool = False) -> rich.console.Console:
    """
    Set up and return the console for printing messages.

    Parameters
    ----------
    no_format : bool
        Whether to disable formatting. Defaults to False.
    quiet : bool
        Whether to suppress console output. Defaults to False.

    Returns
    -------
    rich.console.Console
        The configured rich console object.
    """
    if not no_format:
        install_rich_tracebacks()
    console = rich_console(quiet=quiet, no_color=(no_format or quiet))
    return console


def get_boolean_prompt_function(enable_format: bool = True) -> Callable[[str], bool]:
    """
    Return a function that prompts Y/N and returns True/False.

    Parameters
    ----------
    enable_format : bool
        If True, uses rich's Confirm.ask. If False, uses a plain input prompt.

    Returns
    -------
    Callable[[str], bool]
        A function that takes a question string and returns a boolean.
    """
    if enable_format:
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


def setup_messages(enable_format: bool, quiet: bool) -> None:
    """
    Set up global objects for outputting messages to the CLI.

    Parameters
    ----------
    enable_format : bool
        Whether to enable rich formatting for output.
    quiet : bool
        Whether to suppress console output.
    """
    global open  # noqa: PLW0603
    global boolean_prompt  # noqa: PLW0603
    global RichConsole  # noqa: PLW0603
    global print  # noqa: PLW0603
    open = get_rich_opener(no_format=not enable_format)  # noqa: A001
    RichConsole = setup_console(no_format=not enable_format, quiet=quiet)
    print = RichConsole.print if enable_format else print  # noqa: A001
    boolean_prompt = get_boolean_prompt_function(enable_format=enable_format)


open = get_rich_opener()  # noqa: A001
RichConsole = setup_console()
print = RichConsole.print  # noqa: A001
boolean_prompt = get_boolean_prompt_function()

"""Handle outputs/inputs to the CLI.

The CLI writes through three channels, set up by :func:`setup_messages`:

- ``RichConsole`` -- ordinary status and warnings, on stdout. Silenced by
  ``--quiet``.
- ``error_console`` -- errors, on stderr. Never silenced, so failures remain
  visible under ``--quiet``.
- :func:`payload_print` -- data the user explicitly asked for
  (``--output-to-console``, ``-c``, ``--version``), on stdout, unformatted and
  never silenced.
"""

from __future__ import annotations

import functools
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


def get_rich_opener(
    console: rich.console.Console | None = None,
    disable: bool = False,
) -> Callable[..., Any]:
    """
    Return a file opener that renders a rich progress bar on ``console``.

    Parameters
    ----------
    console : rich.console.Console | None
        Console the progress bar is rendered on. ``None`` lets rich fall back
        to its global console, which is unaware of brassy's output settings.
        Defaults to None.
    disable : bool
        Whether to suppress the progress display entirely. Defaults to False.

    Returns
    -------
    Callable[..., Any]
        A context-manager factory with the call signature of
        :func:`rich.progress.open`.
    """
    return functools.partial(rich.progress.open, console=console, disable=disable)


def setup_console(
    no_format: bool = False,
    quiet: bool = False,
    color: bool = True,
    stderr: bool = False,
) -> rich.console.Console:
    """
    Set up and return a console for printing messages.

    Parameters
    ----------
    no_format : bool
        Whether to disable rich formatting (markup rendering stays on so that
        markup tags are not printed literally). Defaults to False.
    quiet : bool
        Whether to suppress this console's output. Defaults to False.
    color : bool
        Whether to allow ANSI colour and styling. When False, or when
        ``no_format`` is True, the console emits no escape sequences at all.
        Defaults to True.
    stderr : bool
        Whether the console writes to stderr instead of stdout. Defaults to
        False.

    Returns
    -------
    rich.console.Console
        The configured rich console object.
    """
    if not no_format:
        install_rich_tracebacks()
    return rich_console(
        quiet=quiet,
        color_system="auto" if (color and not no_format) else None,
        stderr=stderr,
    )


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


def payload_print(content: str) -> None:
    """
    Write requested program data to stdout, unformatted and never suppressed.

    Parameters
    ----------
    content : str
        Text to write verbatim.
    """
    print(content)


def setup_messages(enable_format: bool, quiet: bool, color: bool = True) -> None:
    """
    Set up the module-level output channels used by the CLI.

    Parameters
    ----------
    enable_format : bool
        Whether to enable rich formatting for output.
    quiet : bool
        Whether to suppress ordinary (non-error) output.
    color : bool
        Whether to allow ANSI colour and styling. Defaults to True.
    """
    global open_with_progress  # noqa: PLW0603
    global boolean_prompt  # noqa: PLW0603
    global RichConsole  # noqa: PLW0603
    global error_console  # noqa: PLW0603
    RichConsole = setup_console(no_format=not enable_format, quiet=quiet, color=color)
    error_console = setup_console(
        no_format=not enable_format,
        quiet=False,
        color=color,
        stderr=True,
    )
    open_with_progress = get_rich_opener(
        console=RichConsole,
        disable=quiet or not enable_format,
    )
    boolean_prompt = get_boolean_prompt_function(enable_format=enable_format)


RichConsole = setup_console()
error_console = setup_console(stderr=True)
open_with_progress = get_rich_opener(console=RichConsole)
boolean_prompt = get_boolean_prompt_function()

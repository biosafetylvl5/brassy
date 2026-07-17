"""Create a release-note YAML template and optionally open it in an editor."""

from __future__ import annotations

from typing import Any

from brassy.utils import (
    editor_handler,
    file_handler,
)


def create_note(  # noqa: PLR0913
    file_path_arg: str | None,
    console: Any,
    working_dir: str = ".",
    open_editor: bool = False,
    editor_override: str | None = None,
    error_console: Any = None,
    force: bool = False,
) -> None:
    """
    Create a blank release-note YAML template and optionally open it.

    The template is always created via
    :func:`brassy.utils.file_handler.create_blank_template_yaml_file`. When
    ``open_editor`` is ``True``, the resulting file is then launched in the
    user's editor (resolved git-style by
    :func:`brassy.utils.editor_handler.resolve_editor`).

    Parameters
    ----------
    file_path_arg : str | None
        The file path of the YAML template as passed via the CLI. ``None``
        derives a name from the current git branch.
    console : Any
        A Rich console used for status messages.
    working_dir : str
        The working directory path. Defaults to the current directory ".".
    open_editor : bool
        Whether to launch the editor on the created file. ``False`` (the
        default) preserves the historical behaviour of ``-t``.
    editor_override : str | None
        An editor command that bypasses resolution, typically sourced from the
        ``--editor`` CLI flag. ``None`` resolves the editor normally.
    error_console : Any
        A Rich console used for error messages. Defaults to ``console`` when
        None.
    force : bool
        Whether to overwrite an existing template file. Defaults to False.

    Notes
    -----
    The editor is launched in the foreground so that interactive editors
    (``vim``, ``nano``, etc.) work correctly. A nonzero editor exit code is
    reported as a warning rather than propagated, since the file creation
    itself succeeded.
    """
    if error_console is None:
        error_console = console
    yaml_path = file_handler.create_blank_template_yaml_file(
        file_path_arg,
        error_console,
        working_dir=working_dir,
        force=force,
    )
    if not open_editor:
        return
    editor = editor_handler.resolve_editor(editor_override)
    # soft_wrap keeps this status line intact: without it rich wraps to the
    # console width (80 cols when output is captured), which splits the message
    # mid-phrase whenever the path is long — e.g. on Windows temp paths.
    console.print(
        f"[green]Created [bold]{yaml_path}[/], opening in '{editor}'...",
        soft_wrap=True,
    )
    exit_code = editor_handler.launch_editor(yaml_path, editor, error_console)
    if exit_code != 0 and exit_code is not None:
        console.print(
            f"[yellow]Editor exited with code {exit_code}; the template at "
            f"{yaml_path} was still created.",
        )

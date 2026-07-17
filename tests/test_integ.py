"""
Integration tests for the Brassy CLI.

This module contains pytest tests for the CLI. It tests the
help display, building from test inputs, template creation,
and pruning behavior.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

test_path = Path(__file__).resolve().parent
input_path = test_path / "inputs"
valid_outputs_path = test_path / "outputs"


def run_cli_command_return_true_if_command_returns_zero(command):
    """Run a CLI command and return True when it succeeds.

    This helper runs the given command using subprocess.run and returns
    True only if the exit status is zero.

    Parameters
    ----------
    command : sequence[str]
        Command and arguments to execute.

    Returns
    -------
    bool
        True if the command's return code is 0, otherwise False.
    """
    result = subprocess.run(command, capture_output=True, text=True, check=False)  # noqa: S603
    assert result.returncode == 0, (
        f"Command failed with return code {result.returncode}"
    )
    return result.returncode == 0


@pytest.mark.integration
def test_help(monkeypatch):  # noqa: ARG001
    """Test the CLI help option.

    Invoke brassy with -h and verify a successful exit.
    """
    run_cli_command_return_true_if_command_returns_zero(["brassy", "-h"])


@pytest.mark.integration
@pytest.mark.parametrize(
    "input_file",
    ["barebones", "mostly-featured", "fully-featured", "real-world", "multi-entry"],
)
def test_build_on_test_files(input_file):
    """Build outputs for predefined test inputs.

    For each input file, run brassy and compare the generated
    RST with the expected output file.
    """
    with tempfile.TemporaryDirectory() as output_file_dir:
        output_file = Path(output_file_dir) / f"{input_file}.rst"
        print(output_file)
        if not run_cli_command_return_true_if_command_returns_zero(
            [
                "brassy",
                str(input_path / f"{input_file}.yaml"),
                "--output-file",
                output_file,
                "--release-date",
                "2024-10-14",
            ],
        ):
            raise OSError("Brassy command failed")
        assert output_file.read_text(encoding="utf-8") == (
            valid_outputs_path / f"{input_file}.rst"
        ).read_text(encoding="utf-8")


def test_create_template_build_template():
    """Test template creation and subsequent build.

    Create a template with -t and then build using the generated file.
    """
    with tempfile.TemporaryDirectory() as output_file_dir:
        output_file = str(Path(output_file_dir) / "template.yaml")
        if not run_cli_command_return_true_if_command_returns_zero(
            ["brassy", "-t", output_file],
        ):
            raise OSError("Brassy command failed")
        if not run_cli_command_return_true_if_command_returns_zero(
            ["brassy", output_file],
        ):
            raise OSError("Brassy command failed")


def test_pruning():
    """Test pruning of a YAML file.

    Copy a sample and prune it with --prune, then compare with the
    expected pruned output.
    """
    with tempfile.TemporaryDirectory() as output_file_dir:
        to_prune = Path(output_file_dir) / "pruned.yaml"
        shutil.copyfile(input_path / "to-prune.yaml", to_prune)

        run_cli_command_return_true_if_command_returns_zero(
            ["brassy", "--prune", to_prune],
        )
        assert to_prune.read_text(encoding="utf-8") == (
            valid_outputs_path / "pruned.yaml"
        ).read_text(encoding="utf-8")


DUPLICATE_KEY_YAML = """\
bug fix:
- title: 'First entry'
  description: 'first'
bug fix:
- title: 'Second entry'
  description: 'second'
"""


@pytest.mark.integration
def test_build_rejects_duplicate_keys():
    """Building a file with a duplicate category fails loudly.

    Without this check the first entry is silently dropped and brassy
    still exits zero.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        dupe = Path(work_dir) / "dupe.yaml"
        dupe.write_text(DUPLICATE_KEY_YAML)

        result = subprocess.run(  # noqa: S603
            ["brassy", str(dupe), "--release-date", "2024-10-14"],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0
        assert "Duplicate key 'bug fix'" in result.stdout + result.stderr


@pytest.mark.integration
def test_prune_rejects_duplicate_keys_without_touching_file():
    """Pruning a file with a duplicate key fails and leaves it unmodified.

    --prune rewrites in place, so bailing out before the write is what
    keeps the dropped entry from being destroyed on disk.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        dupe = Path(work_dir) / "dupe.yaml"
        dupe.write_text(DUPLICATE_KEY_YAML)

        result = subprocess.run(  # noqa: S603
            ["brassy", "--prune", str(dupe)],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0
        assert "Duplicate key 'bug fix'" in result.stdout + result.stderr
        assert dupe.read_text() == DUPLICATE_KEY_YAML


def test_template_output():
    """Test outputting a template file.

    Create a template file and compare it to the output.
    """
    with tempfile.TemporaryDirectory() as output_file_dir:
        output_file = Path(output_file_dir) / "template-output.yaml"
        run_cli_command_return_true_if_command_returns_zero(
            ["brassy", "--write-yaml-template", str(output_file)],
        )
        assert output_file.read_text(encoding="utf-8") == (
            valid_outputs_path / "template-output.yaml"
        ).read_text(encoding="utf-8")


def _run_with_env(command, env_overrides):
    """Run a CLI command with extra environment variables.

    Parameters
    ----------
    command : sequence[str]
        Command and arguments to execute.
    env_overrides : dict[str, str]
        Environment variables to set for the subprocess, merged on top of
        the current process environment.

    Returns
    -------
    subprocess.CompletedProcess
        The completed subprocess result.
    """
    env = {**dict(os.environ), **env_overrides}
    return subprocess.run(  # noqa: S603
        command,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


_EDITOR_TRUE_ENV = {
    "BRASSY_AUTO_OPEN_EDITOR": "true",
    "BRASSY_DEFAULT_EDITOR": "true",
}


@pytest.mark.integration
def test_create_template_opens_editor():
    """Test that -t opens the editor when auto_open_editor is enabled.

    With ``auto_open_editor=true`` and every editor source set to ``true``
    (the ``true`` binary exits 0 immediately), ``brassy -t`` should create
    the template, launch the editor, and exit 0.
    """
    with tempfile.TemporaryDirectory() as output_file_dir:
        output_file = str(Path(output_file_dir) / "template.yaml")
        result = _run_with_env(
            ["brassy", "-t", output_file],
            _EDITOR_TRUE_ENV,
        )
        assert result.returncode == 0, (
            f"Command failed with return code {result.returncode}: "
            f"{result.stdout}\n{result.stderr}"
        )
        assert Path(output_file).exists()
        assert "opening in" in result.stdout, (
            f"Editor should have been launched; stdout: {result.stdout}"
        )


@pytest.mark.integration
def test_create_template_no_open_override():
    """Test that --no-open suppresses the editor even when enabled.

    With ``auto_open_editor=true`` set, passing ``--no-open`` should still
    create the template without launching the editor.
    """
    with tempfile.TemporaryDirectory() as output_file_dir:
        output_file = str(Path(output_file_dir) / "template.yaml")
        result = _run_with_env(
            ["brassy", "-t", output_file, "--no-open"],
            _EDITOR_TRUE_ENV,
        )
        assert result.returncode == 0, (
            f"Command failed with return code {result.returncode}: "
            f"{result.stdout}\n{result.stderr}"
        )
        assert Path(output_file).exists()
        assert "opening in" not in result.stdout, (
            f"Editor should NOT have been launched; stdout: {result.stdout}"
        )


@pytest.mark.integration
def test_create_template_editor_flag():
    """Test that --editor overrides the resolved editor command.

    With ``default_editor=false`` in the environment (would fail), passing
    ``--editor true`` should override it and the command should succeed.
    """
    with tempfile.TemporaryDirectory() as output_file_dir:
        output_file = str(Path(output_file_dir) / "template.yaml")
        result = _run_with_env(
            ["brassy", "-t", output_file, "--editor", "true"],
            {
                "BRASSY_AUTO_OPEN_EDITOR": "true",
                "BRASSY_DEFAULT_EDITOR": "false",
            },
        )
        assert result.returncode == 0, (
            f"Command failed with return code {result.returncode}: "
            f"{result.stdout}\n{result.stderr}"
        )
        assert Path(output_file).exists()
        assert "opening in 'true'" in result.stdout, (
            f"Editor should have been overridden to 'true'; stdout: {result.stdout}"
        )


@pytest.mark.integration
def test_visual_takes_priority_over_editor():
    """Test that $VISUAL outranks $EDITOR in the resolution chain.

    With ``$VISUAL=echo`` and ``$EDITOR=false`` (the ``false`` binary
    exits 1), the resolution should pick ``echo`` over ``false``,
    verifying the documented priority: ``$VISUAL`` > ``$EDITOR``.
    """
    with tempfile.TemporaryDirectory() as output_file_dir:
        output_file = str(Path(output_file_dir) / "template.yaml")
        result = _run_with_env(
            ["brassy", "-t", output_file],
            {
                "BRASSY_AUTO_OPEN_EDITOR": "true",
                "VISUAL": "echo",
                "EDITOR": "false",
            },
        )
        assert result.returncode == 0, (
            f"Command failed with return code {result.returncode}: "
            f"{result.stdout}\n{result.stderr}"
        )
        assert Path(output_file).exists()
        assert "opening in 'echo'" in result.stdout, (
            f"VISUAL should have been resolved as the editor; stdout: {result.stdout}"
        )

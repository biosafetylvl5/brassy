"""
Integration tests for the Brassy CLI.

This module contains pytest tests for the CLI. It tests the
help display, building from test inputs, template creation,
and pruning behavior.
"""

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
    ["barebones", "mostly-featured", "fully-featured", "real-world"],
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
        assert list(output_file.open()) == list(
            (valid_outputs_path / f"{input_file}.rst").open(),
        )


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
        assert list(to_prune.open()) == list(
            (valid_outputs_path / "pruned.yaml").open(),
        )

def test_template_output():
    """Test outputting a template file.

    Create a template file and compare it to the output.
    """
    with tempfile.TemporaryDirectory() as output_file_dir:
        output_file = Path(output_file_dir) / "template-output.yaml"
        run_cli_command_return_true_if_command_returns_zero(
            ["brassy", "--write-yaml-template", str(output_file)],
        )
        assert list(output_file.open()) == list(
            (valid_outputs_path / "template-output.yaml").open(),
        )

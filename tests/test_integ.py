import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

test_path = Path(__file__).resolve().parent
input_path = test_path / "inputs"
valid_outputs_path = test_path / "outputs"


def run_cli_command_return_true_if_command_returns_zero(command):
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert (
        result.returncode == 0
    ), f"Command failed with return code {result.returncode}"
    return result.returncode == 0


@pytest.mark.integtest
def test_help(monkeypatch):
    run_cli_command_return_true_if_command_returns_zero(["brassy", "-h"])


@pytest.mark.integtest
@pytest.mark.parametrize(
    "input_file", ["barebones", "mostly-featured", "fully-featured"],
)
def test_build_on_test_files(input_file):
    with tempfile.TemporaryDirectory() as output_file_dir:
        output_file_dir = Path(output_file_dir)
        output_file = output_file_dir / f"{input_file}.rst"
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
        assert list(output_file.open()) == list((valid_outputs_path / f"{input_file}.rst").open())


def test_create_template_build_template():
    with tempfile.TemporaryDirectory() as output_file_dir:
        output_file_dir = Path(output_file_dir)
        output_file = str(output_file_dir / "template.yaml")
        if not run_cli_command_return_true_if_command_returns_zero(
            ["brassy", "-t", output_file],
        ):
            raise OSError("Brassy command failed")
        if not run_cli_command_return_true_if_command_returns_zero(
            ["brassy", output_file],
        ):
            raise OSError("Brassy command failed")


def test_pruning():
    with tempfile.TemporaryDirectory() as output_file_dir:
        output_file_dir = Path(output_file_dir)
        to_prune = output_file_dir / "pruned.yaml"
        shutil.copyfile(input_path / "to-prune.yaml", to_prune)

        run_cli_command_return_true_if_command_returns_zero(
            ["brassy", "--prune", to_prune],
        )
        assert list(to_prune.open()) == list((valid_outputs_path / "pruned.yaml").open())

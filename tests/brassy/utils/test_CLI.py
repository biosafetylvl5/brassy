"""
Tests for brassy.utils.CLI argument handling.

These cover the argument-parsing defects behind two user-visible symptoms:
a --no-color flag whose default is inverted and which nothing ever reads,
and a validation guard that never fires because it consults the wrong
attribute.
"""

import sys
from pathlib import Path

import pytest
from rich.console import Console

# Ensure we can import from src/
ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    src = parent / "src"
    if src.is_dir():
        sys.path.insert(0, str(src))
        break

import brassy.utils.CLI  # noqa: E402
from brassy.utils.CLI import exit_on_invalid_arguments, get_parser  # noqa: E402


def test_no_color_defaults_to_false():
    """Not passing --no-color must leave no_color False.

    The default is Settings.use_color, which ships as True, so the flag reads
    True whether or not the user asked for it. The default of a "--no-x" flag
    is the one value it cannot sensibly take: the state that means "the user
    asked for no-x".
    """
    assert get_parser().parse_args([]).no_color is False


def test_no_color_is_true_when_passed():
    """Passing --no-color must set no_color True.

    Currently vacuous -- no_color is True either way -- but it stops the test
    above from being satisfied by flipping the default and breaking the flag
    in the other direction.
    """
    assert get_parser().parse_args(["-nc"]).no_color is True


@pytest.mark.parametrize("use_color", [True, False])
def test_no_color_default_ignores_the_use_color_setting(monkeypatch, use_color):
    """A config setting must not decide what "flag absent" means.

    use_color is a legitimate setting, but it belongs wherever colour is
    turned on, not in the default of the flag that overrides it. Wiring it
    here is what inverts the flag, so the default tracks the setting instead
    of staying put: the use_color=True case fails today, and it is the one
    every user gets, since True is the shipped default.
    """
    monkeypatch.setattr(brassy.utils.CLI.Settings, "use_color", use_color)

    assert get_parser().parse_args([]).no_color is False


def test_bare_arguments_are_rejected():
    """exit_on_invalid_arguments must reject an empty invocation.

    The guard tests args.version, but -r/--release-version claims dest
    "version" and defaults to "[UNKNOWN]". That is always truthy, so the
    function always returns early and the exit(1) below it is dead code. The
    flag the guard means to read is args.print_version.
    """
    parser = get_parser()
    args = parser.parse_args([])

    with pytest.raises(SystemExit) as exc_info:
        exit_on_invalid_arguments(args, parser, Console(quiet=True))

    assert exc_info.value.code != 0


def test_release_version_flag_does_not_satisfy_the_guard():
    """Supplying -r alone is still not a runnable command.

    Naming a version to stamp on release notes says nothing about which notes
    to build, so -r must not on its own make the invocation valid. It does
    today, by the same dest collision.
    """
    parser = get_parser()
    args = parser.parse_args(["-r", "1.2.3"])

    with pytest.raises(SystemExit):
        exit_on_invalid_arguments(args, parser, Console(quiet=True))


def test_version_flag_satisfies_the_guard():
    """--version alone is a complete command and must be allowed through.

    The counterpart to the tests above: once the guard reads print_version
    rather than version, this is the case it has to keep accepting.
    """
    parser = get_parser()
    args = parser.parse_args(["--version"])

    exit_on_invalid_arguments(args, parser, Console(quiet=True))

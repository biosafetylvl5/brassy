"""Wrapper for CLI call and top-level functions."""

from __future__ import annotations

from brassy.utils import settings_manager

Settings = settings_manager.get_settings("brassy")


def run_from_CLI(): # noqa: N802
    from brassy.utils import CLI  # noqa: PLC0415 # here to prevent circular import
    CLI.run_from_CLI()


if __name__ == "__main__":
    run_from_CLI()

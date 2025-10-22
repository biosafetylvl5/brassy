"""
This module provides functionality to generate release notes from YAML files.
It reads YAML files, parses their content, and formats the parsed data into release notes in .rst format.
The release notes can be written to an output file.
"""


from __future__ import annotations

from brassy.utils import settings_manager

Settings = settings_manager.get_settings("brassy")


def run_from_CLI():
    from brassy.utils import CLI

    CLI.run_from_CLI()


if __name__ == "__main__":
    run_from_CLI()

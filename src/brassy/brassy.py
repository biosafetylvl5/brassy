"""
This module provides functionality to generate release notes from YAML files.
It reads YAML files, parses their content, and formats the parsed data into release notes in .rst format.
The release notes can be written to an output file.
"""

import argparse
import os
import rich.progress
import yaml
from datetime import datetime

import pygit2

import brassy.utils.settings_manager as settings_manager

Settings = settings_manager.get_settings("brassy")

import brassy.utils.CLI


run_from_CLI = brassy.utils.CLI.run_from_CLI
if __name__ == "__main__":
    run_from_CLI()

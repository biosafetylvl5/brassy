# This module is for the CLI only portions of brassy.
# Brassy can be run without this file, and importing it should

import argparse
import os

from rich_argparse import RichHelpFormatter
import brassy.actions
import brassy.actions.build_release_notes
import brassy.actions.init
import brassy.actions.prune_yaml
import brassy.utils.file_handler
import brassy.utils.git_handler
from brassy.utils.settings_manager import get_settings
import brassy.utils.messages as messages

Settings = get_settings("brassy")


def get_parser():
    """
    Returns an ArgumentParser object with predefined arguments for generating release notes from YAML files.

    Returns:
        argparse.ArgumentParser: The ArgumentParser object with predefined arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generate release notes from YAML files."
        + " Entries are sorted by order in yaml files, "
        + "and by order of yaml files provided via the command line.",
        formatter_class=RichHelpFormatter,
    )
    parser.add_argument(
        "-t",
        "--write-yaml-template",
        type=str,
        help="Write template YAML to provided file."
        + " If folder provided, place template in folder with current "
        + "git branch name as file name.",
        nargs="?",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-c",
        "--get-changed-files",
        type=str,
        help="Print git tracked file changes against main."
        + " If directory provided, use that directories checked-out branch.",
        nargs="?",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "input_files_or_folders",
        type=str,
        nargs="*",
        help="The folder(s) containing YAML files and/or YAML files. "
        + "Folders will be searched recursively.",
    )
    parser.add_argument(
        "-r",
        "--release-version",
        type=str,
        default="[UNKNOWN]",
        help="Version number of the release. Default is '[UNKNOWN]'.",
        required=False,
        dest="version",
    )
    parser.add_argument(
        "-d",
        "--release-date",
        type=str,
        help="Date of the release. Default is current system time.",
        required=False,
    )
    parser.add_argument(
        "-nc",
        "--no-color",
        action="store_true",
        default=Settings.use_color,
        help="Disable text formatting for CLI output.",
    )
    parser.add_argument(
        "-p",
        "--prefix-file",
        type=str,
        help="A header file to prepend to the release notes.",
    )
    parser.add_argument(
        "-s",
        "--suffix-file",
        type=str,
        help="A footer file to suffix to the release notes.",
    )
    parser.add_argument(
        "-o", "--output-file", type=str, help="The output file for release notes."
    )
    if Settings.default_yaml_path and Settings.enable_experimental_features:
        yaml_path = os.path.join(".", Settings.default_yaml_path)
    else:
        yaml_path = "."
    parser.add_argument(
        "-yd",
        "--yaml-dir",
        type=str,
        help="Directory to write yaml files to",
        default=yaml_path,
    )
    parser.add_argument(
        "--output-to-console",
        action="store_true",
        default=False,
        help="Write generated release notes to console.",
    )
    parser.add_argument(
        "-nr", "--no-rich", action="store_true", help="Disable rich text output"
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Only output errors")
    parser.add_argument(
        "-pr", "--prune", action="store_true", help="Prune provided files, do not build"
    )
    parser.add_argument(
        "--init", action="store_true", help="Initialize brassy", default=False
    )
    return parser


def parse_arguments():
    """
    Parse command line arguments for input folder and output file.

    Returns
    -------
    argparse.Namespace
        Parsed arguments containing input_folder and output_file.
    """
    parser = get_parser()
    return parser.parse_args(), parser


def exit_on_invalid_arguments(args, parser, console):
    """
    Validate the argparse arguments.

    This function validates the provided argparse arguments to ensure
    that the required input files/folders and output file are provided.
    If arguments are invalid, it prints an error message and exits the program.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed arguments.

    parser : argparse.ArgumentParser
        The ArgumentParser object used to parse the command-line arguments.
    """
    if bool(args.input_files_or_folders) or "get_changed_files" in args or args.init:
        return

    if "write_yaml_template" in args:
        return

    console.print("[bold red]Invalid arguments.\n")
    parser.print_help()
    exit(1)


def get_yaml_files_from_input(input_files_or_folders):
    """
    Get a list of YAML files from the given input files or folders.

    Parameters
    ----------
    input_files_or_folders : list
        List of paths to input files or folders.

    Returns
    -------
    list
        List of paths to YAML files.

    Raises
    ------
    ValueError
        If a file is not a YAML file or if no YAML files are found in a directory.
    """
    yaml_files = []
    for path in input_files_or_folders:
        if os.path.isfile(path):
            if not path.endswith(".yaml") or path.endswith(".yml"):
                raise ValueError(f"File {path} is not a YAML file.")
            yaml_files.append(path)
        elif os.path.isdir(path):
            dir_yaml_files = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".yaml") or file.endswith(".yml"):
                        dir_yaml_files.append(os.path.join(root, file))
            if len(dir_yaml_files) == 0:
                raise FileExistsError(f"No YAML files found in directory {path}.")
            yaml_files.extend(dir_yaml_files)
        else:
            raise FileNotFoundError(path)
    return yaml_files


def get_file_list_from_cli_input(input_files_or_folders, console, working_dir="."):
    try:
        yaml_files = get_yaml_files_from_input(
            [
                brassy.utils.file_handler.get_yaml_template_path(
                    path, working_dir=working_dir
                )
                for path in input_files_or_folders
            ]
        )
    except FileExistsError as e:
        if Settings.fail_on_empty_dir:
            console.print(f"[red]Invalid file or directory: [bold]{e}[/]")
            exit(1)
        else:
            console.print(f"[yellow]Invalid file or directory: [bold]{e}[/]")
            console.print(
                f"[yellow]Returning 0 because fail_on_empty_dir is [bold]False[/]"
            )
            exit(0)
    except FileNotFoundError as e:
        console.print(f"[red]Invalid file or directory: [bold]{e}[/]")
        exit(1)
    except ValueError as e:
        console.print(f"[red]{e}")
        exit(1)
    return yaml_files


def run_from_CLI():
    """
    Main function to generate release notes from YAML files and write to an output file.
    """
    args, parser = parse_arguments()

    messages.setup_messages(format=not args.no_rich, quiet=args.quiet)

    console = messages.RichConsole
    printer = messages.print
    rich_open = messages.open

    exit_on_invalid_arguments(args, parser, console)
    if args.init:
        brassy.actions.init.init()
        exit(0)
    elif args.prune:
        brassy.actions.prune_yaml.direct_pruning_of_files(
            args.input_files_or_folders, console, args.yaml_dir
        )
    elif "write_yaml_template" in args:
        brassy.utils.file_handler.create_blank_template_yaml_file(
            args.write_yaml_template,
            console,
            working_dir=args.yaml_dir,
        )
    elif "get_changed_files" in args:
        brassy.utils.git_handler.print_out_git_changed_files(
            printer,
            repo_path=args.get_changed_files if args.get_changed_files else ".",
        )
    elif args.input_files_or_folders:
        content = brassy.actions.build_release_notes.build_release_notes(
            args.input_files_or_folders,
            console,
            rich_open,
            version=args.version,
            release_date=args.release_date,
            header_file=args.prefix_file,
            footer_file=args.suffix_file,
            working_dir=args.yaml_dir,
        )
        if args.output_file:
            brassy.utils.file_handler.write_output_file(args.output_file, content)
            if not args.quiet:
                console.print(f"[green]Wrote release notes to {args.output_file}")
        else:
            if not args.quiet:
                console.print(
                    f"[green]Release notes built successfully. No output file provided."
                )
        if args.output_to_console:
            console.print(content)

    else:
        parser.print_help()

"""Handle Git-related functionality."""

from __future__ import annotations

import string
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

import pygit2

# Base branches tried, in order, when none is explicitly configured.
_DEFAULT_BASE_BRANCHES = ("main", "master", "trunk")


def _resolve_base_branch(
    repo: pygit2.Repository, base_branch: str | None,
) -> pygit2.Branch:
    """
    Resolve the base branch to diff against.

    Parameters
    ----------
    repo : pygit2.Repository
        The repository to look the branch up in.
    base_branch : str | None
        An explicit base branch name. When None, the branches in
        ``_DEFAULT_BASE_BRANCHES`` are tried in order.

    Returns
    -------
    pygit2.Branch
        The resolved base branch.

    Raises
    ------
    pygit2.GitError
        If the explicit branch is missing, or none of the default branches
        exist.
    """
    if base_branch is not None:
        try:
            return repo.branches[base_branch]
        except KeyError as e:
            raise pygit2.GitError(
                f"Base branch '{base_branch}' not found in {repo.workdir}.",
            ) from e
    for candidate in _DEFAULT_BASE_BRANCHES:
        try:
            return repo.branches[candidate]
        except KeyError:
            continue
    tried = ", ".join(_DEFAULT_BASE_BRANCHES)
    raise pygit2.GitError(
        f"No base branch found (tried {tried}). "
        "Pass --base-branch or set the 'base_branch' setting.",
    )


def get_git_status(
    repo_path: str = ".", base_branch: str | None = None,
) -> dict[str, list[Any]]:
    """
    Retrieve the status of files in the specified Git repository.

    Parameters
    ----------
    repo_path : str
        The path to the Git repository. Defaults to the current directory.
    base_branch : str | None
        The branch to diff the current branch against. When None, brassy tries
        ``main``, ``master``, then ``trunk``.

    Returns
    -------
    dict[str, list[Any]]
        A dictionary with the following keys:

        - added : list of str
            List of file paths for files that have been added.
        - modified : list of str
            List of file paths for files that have been modified.
        - deleted : list of str
            List of file paths for files that have been deleted.
        - moved : list of tuple
            List of (old_path, new_path) tuples for renamed files.

    Raises
    ------
    pygit2.GitError
        If the repository path is not a git repository, has no HEAD, or no
        base branch could be resolved.
    """
    # Open the repository
    repo = pygit2.Repository(repo_path)

    # Get the current branch reference
    try:
        current_branch = repo.head
    except pygit2.GitError as e:
        raise pygit2.GitError(
            f"{repo_path} is not a git repo or does not have a head") from e

    # Get the base branch reference
    main_branch = _resolve_base_branch(repo, base_branch)

    # Get the commit objects
    current_commit = repo[current_branch.target]
    main_commit = repo[main_branch.target]

    # Get the diff between the current commit and the base branch commit
    diff = repo.diff(main_commit, current_commit)

    # Prepare dictionaries to store file statuses
    status = {
        "added": [],
        "modified": [],
        "deleted": [],
        "moved": [],
    }

    # Process the diff
    for delta in diff.deltas:
        if delta.status == pygit2.GIT_DELTA_ADDED:
            status["added"].append(delta.new_file.path)
        elif delta.status == pygit2.GIT_DELTA_MODIFIED:
            status["modified"].append(delta.new_file.path)
        elif delta.status == pygit2.GIT_DELTA_DELETED:
            status["deleted"].append(delta.old_file.path)
        elif delta.status == pygit2.GIT_DELTA_RENAMED:
            status["moved"].append((delta.old_file.path, delta.new_file.path))

    return {
        "added": status["added"],
        "modified": status["modified"],
        "deleted": status["deleted"],
        "moved": status["moved"],
    }


def print_out_git_changed_files(
    print_function: Callable[[str], None],
    repo_path: str = ".",
    base_branch: str | None = None,
) -> None:
    """
    Print out changes as detected by Git in format Brassy expects in changlogs.

    Parameters
    ----------
    print_function : Callable[[str], None]
        A callable that takes a string and prints it.
    repo_path : str
        The path to the Git repository. Defaults to the current directory.
    base_branch : str | None
        The branch to diff against. When None, brassy tries ``main``,
        ``master``, then ``trunk``.
    """
    status = get_git_status(repo_path=repo_path, base_branch=base_branch)
    for entry in status:
        print_function(f"    {entry}:")
        for file in status[entry]:
            print_function(f"    - '{file}'")


def get_current_git_branch(sanitize: bool = True) -> str:
    """
    Get the current dirs git branch name.

    Parameters
    ----------
    sanitize : bool
        If True, sanitize branch name as a valid file name before returning.

    Returns
    -------
    str
        The name of the current git branch.
    """
    repo = pygit2.Repository(".")
    branch = repo.head.shorthand
    if sanitize:
        valid_characters = "-_." + string.ascii_letters + string.digits
        return ''.join(c if c in valid_characters else "-" for c in branch)
    else:
        return branch

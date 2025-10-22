import pygit2


def get_git_status(repo_path="."):
    """
    Retrieve the status of files in the specified Git repository.

    Parameters
    ----------
    repo_path : str, optional
        The path to the Git repository. Defaults to the current directory.

    Returns
    -------
    dict
        A dictionary with the following keys:

        - 'added': list of str
            List of file paths for files that have been added.
        - 'modified': list of str
            List of file paths for files that have been modified.
        - 'deleted': list of str
            List of file paths for files that have been deleted.
        - 'renamed': list of str
            List of file paths for files that have been renamed.
    """
    # Open the repository
    repo = pygit2.Repository(repo_path)

    # Get the current branch reference
    try:
        current_branch = repo.head
    except pygit2.GitError:
        raise pygit2.GitError(f"{repo_path} is not a git repo or does not have a head")

    # Get the main branch reference
    main_branch = repo.branches["main"]

    # Get the commit objects
    current_commit = repo[current_branch.target]
    main_commit = repo[main_branch.target]

    # Get the diff between the current commit and the main branch commit
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


def print_out_git_changed_files(print_function, repo_path="."):
    status = get_git_status(repo_path=repo_path)
    for entry in status:
        print_function(f"    {entry}:")
        for file in status[entry]:
            print_function(f"    - '{file}'")


def get_current_git_branch():
    """
    Get the current dirs git branch name.

    Returns
    -------
    str
        The name of the current git branch.
    """
    repo = pygit2.Repository(".")
    return repo.head.shorthand

"""
Integration tests for command-line usability defects.

Every test in this module currently fails. Each one encodes a behaviour a
user of the ``brassy`` command already depends on, so they are written
against the contract rather than against any particular fix: the intent is
that they pass once the defect is addressed, whichever way it is addressed.
"""

# cSpell:ignore titel

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

EXISTING_NOTE = """\
bug fix:
- title: 'Hand written release note'
  description: 'Work the user does not want silently destroyed.'
  files:
    modified:
    - src/example.py
"""

TYPO_NOTE = """\
bug fix:
- titel: 'title is misspelled here'
  description: 'an otherwise valid entry'
  files:
    modified:
    - src/example.py
"""


def run_brassy(args, env_overrides=None, cwd=None):
    """Run the brassy CLI and return the completed process.

    Parameters
    ----------
    args : sequence[str]
        Arguments to pass to brassy, excluding the program name.
    env_overrides : dict[str, str] | None
        Environment variables merged on top of the current environment.
    cwd : str | Path | None
        Working directory for the subprocess.

    Returns
    -------
    subprocess.CompletedProcess
        The completed subprocess result.
    """
    env = {**dict(os.environ), **(env_overrides or {})}
    return subprocess.run(  # noqa: S603
        ["brassy", *[str(arg) for arg in args]],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
        env=env,
        cwd=None if cwd is None else str(cwd),
    )


def output_of(result):
    """Return a subprocess's combined stdout and stderr.

    Parameters
    ----------
    result : subprocess.CompletedProcess
        A completed subprocess result.

    Returns
    -------
    str
        stdout concatenated with stderr.
    """
    return result.stdout + result.stderr


def make_repo(path, default_branch="main"):
    """Create a git repository with one commit on ``default_branch``.

    Parameters
    ----------
    path : Path
        Directory in which to create the repository.
    default_branch : str
        Name of the initial branch. Defaults to "main".

    Returns
    -------
    Path
        The repository path, for convenience.
    """
    subprocess.run(  # noqa: S603
        ["git", "-c", f"init.defaultBranch={default_branch}", "init", "-q", str(path)],  # noqa: S607
        check=True,
        capture_output=True,
    )
    for key, value in (("user.email", "test@example.com"), ("user.name", "test")):
        subprocess.run(  # noqa: S603
            ["git", "-C", str(path), "config", key, value],  # noqa: S607
            check=True,
            capture_output=True,
        )
    (path / "tracked.txt").write_text("initial\n")
    subprocess.run(  # noqa: S603
        ["git", "-C", str(path), "add", "-A"],  # noqa: S607
        check=True,
        capture_output=True,
    )
    subprocess.run(  # noqa: S603
        ["git", "-C", str(path), "commit", "-qm", "initial"],  # noqa: S607
        check=True,
        capture_output=True,
    )
    return path


def checkout_branch_with_a_change(path, branch):
    """Create ``branch``, add a file on it, and commit.

    Parameters
    ----------
    path : Path
        An existing git repository.
    branch : str
        Name of the branch to create and check out.
    """
    subprocess.run(  # noqa: S603
        ["git", "-C", str(path), "checkout", "-q", "-b", branch],  # noqa: S607
        check=True,
        capture_output=True,
    )
    (path / "added.txt").write_text("new file\n")
    subprocess.run(  # noqa: S603
        ["git", "-C", str(path), "add", "-A"],  # noqa: S607
        check=True,
        capture_output=True,
    )
    subprocess.run(  # noqa: S603
        ["git", "-C", str(path), "commit", "-qm", "add a file"],  # noqa: S607
        check=True,
        capture_output=True,
    )


@pytest.mark.integration
def test_write_template_does_not_clobber_an_existing_file():
    """``-t`` must not destroy a note that already exists at the target path.

    The template is written with mode "w" unconditionally, so re-running the
    command over a populated note replaces it with a blank template. There is
    no prompt and no message, so the loss is silent and unrecoverable.

    Refusing is one valid fix; prompting or writing a backup are others. What
    this test pins down is only that the user's text is not gone afterwards.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        note = Path(work_dir) / "note.yaml"
        note.write_text(EXISTING_NOTE)

        run_brassy(["-t", note])

        assert "Hand written release note" in note.read_text(), (
            "brassy -t overwrote an existing note without warning"
        )


@pytest.mark.integration
def test_write_template_reports_when_it_will_not_overwrite():
    """Declining to overwrite has to be visible and detectable.

    Preserving the file is not enough on its own: a user who believes they
    just created a template needs to be told they did not, and a script needs
    a nonzero status to notice.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        note = Path(work_dir) / "note.yaml"
        note.write_text(EXISTING_NOTE)

        result = run_brassy(["-t", note])

        assert result.returncode != 0
        assert "note.yaml" in output_of(result)


@pytest.mark.integration
def test_branch_named_template_does_not_clobber_existing_notes():
    """``-t`` with no argument is the dangerous case and must be safe too.

    With no path, the filename is derived from the current git branch, so the
    target is identical on every run. Repeating the command -- from shell
    history, or out of habit -- lands on the note written earlier.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        repo = make_repo(Path(work_dir))
        checkout_branch_with_a_change(repo, "feature-work")
        note = repo / "feature-work.yaml"
        note.write_text(EXISTING_NOTE)

        run_brassy(["-t"], cwd=repo)

        assert "Hand written release note" in note.read_text(), (
            "brassy -t overwrote the branch-named note without warning"
        )


@pytest.mark.integration
def test_write_template_into_a_directory_uses_the_branch_name():
    """``-t <existing dir>`` places a branch-named template in that directory.

    The help text has always promised this ("If folder provided, place
    template in folder with current git branch name as file name"); before
    the fix an existing directory hit the overwrite guard with a misleading
    suggestion to pass --force, and --force raised IsADirectoryError.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        repo = make_repo(Path(work_dir))
        checkout_branch_with_a_change(repo, "feature-work")
        notes_dir = repo / "notes"
        notes_dir.mkdir()

        result = run_brassy(["-t", "notes"], cwd=repo)

        assert result.returncode == 0, output_of(result)
        assert (notes_dir / "feature-work.yaml").is_file(), (
            "no branch-named template appeared in the directory"
        )


@pytest.mark.integration
def test_write_template_into_a_directory_still_refuses_to_clobber():
    """The overwrite guard applies to the file inside the directory."""
    with tempfile.TemporaryDirectory() as work_dir:
        repo = make_repo(Path(work_dir))
        checkout_branch_with_a_change(repo, "feature-work")
        notes_dir = repo / "notes"
        notes_dir.mkdir()
        note = notes_dir / "feature-work.yaml"
        note.write_text(EXISTING_NOTE)

        result = run_brassy(["-t", "notes"], cwd=repo)

        assert result.returncode != 0
        assert "Hand written release note" in note.read_text(), (
            "brassy -t overwrote a note inside the target directory"
        )


@pytest.mark.integration
def test_quiet_still_reports_errors():
    """``--quiet`` promises "Only output errors" and must print them.

    The flag is passed to rich's Console(quiet=...), which suppresses all
    output including failures, so the command dies silently. Quiet mode is
    what CI uses, which is where an unexplained nonzero exit costs the most.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        missing = Path(work_dir) / "does-not-exist.yaml"

        result = run_brassy(["--quiet", missing])

        assert result.returncode != 0
        assert output_of(result).strip(), (
            "--quiet exited nonzero but printed nothing at all"
        )
        assert "does-not-exist.yaml" in output_of(result)


@pytest.mark.integration
def test_quiet_suppresses_success_chatter():
    """The other half of the contract: no chatter when nothing is wrong.

    Guards against "fixing" the test above by making --quiet print normally.
    This one already passes; it is here to stay passing.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        note = Path(work_dir) / "note.yaml"
        note.write_text(EXISTING_NOTE)
        output = Path(work_dir) / "out.rst"

        result = run_brassy(["--quiet", note, "-o", output, "-d", "2024-10-14"])

        assert result.returncode == 0
        assert "Wrote release notes" not in output_of(result)


@pytest.mark.integration
def test_quiet_suppresses_the_progress_bar():
    """``--quiet`` must silence progress output on a successful build.

    quiet reaches the message console but not the rich progress opener, so
    the per-file "Reading ..." bar survives it. Together with the test above
    this is exactly backwards: the routine chatter gets through and the
    errors do not.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        note = Path(work_dir) / "note.yaml"
        note.write_text(EXISTING_NOTE)
        output = Path(work_dir) / "out.rst"

        result = run_brassy(["--quiet", note, "-o", output, "-d", "2024-10-14"])

        assert result.returncode == 0
        assert "Reading" not in output_of(result), (
            "--quiet let the progress bar through while suppressing errors"
        )


@pytest.mark.integration
def test_no_color_flag_suppresses_ansi_escapes():
    """``-nc`` has to actually disable colour.

    args.no_color is parsed and never read, so the flag changes nothing. The
    error below is styled red; FORCE_COLOR keeps rich emitting escapes into a
    pipe so the difference is observable off a terminal.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        missing = Path(work_dir) / "does-not-exist.yaml"

        result = run_brassy(["-nc", missing], env_overrides={"FORCE_COLOR": "1"})

        assert "\x1b[" not in output_of(result), (
            "-nc was passed but ANSI colour codes were still emitted"
        )


@pytest.mark.integration
def test_color_is_on_by_default():
    """Without ``-nc``, colour stays on.

    The default for no_color is Settings.use_color, which inverts the flag's
    meaning. This test fails if that inversion is fixed by disabling colour
    everywhere instead of wiring the flag up.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        missing = Path(work_dir) / "does-not-exist.yaml"

        result = run_brassy([missing], env_overrides={"FORCE_COLOR": "1"})

        assert "\x1b[" in output_of(result)


@pytest.mark.integration
def test_bare_invocation_exits_nonzero():
    """Running ``brassy`` with no arguments is a usage error.

    exit_on_invalid_arguments checks args.version, which is the -r release
    version string and defaults to the truthy "[UNKNOWN]", so the guard always
    returns early and the exit(1) below it is unreachable. Bare brassy prints
    help and exits 0, so a caller cannot distinguish misuse from success.
    """
    result = run_brassy([])

    assert result.returncode != 0


@pytest.mark.integration
def test_changed_files_outside_a_main_branch_repo_is_actionable():
    """``-c`` must fail in plain language on a repo with no ``main``.

    The base branch is hardcoded to "main", so a master or trunk repo raises
    KeyError out of pygit2 and prints a full traceback. Every other git
    failure in the codebase is caught and explained; this one should be too,
    whether the fix is a fallback or a clear message.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        repo = make_repo(Path(work_dir), default_branch="master")
        checkout_branch_with_a_change(repo, "feature-work")

        result = run_brassy(["-c"], cwd=repo)

        combined = output_of(result)
        assert "KeyError" not in combined, "a raw KeyError traceback reached the user"
        assert "Traceback" not in combined
        if result.returncode != 0:
            assert "branch" in combined.lower()


@pytest.mark.integration
def test_invalid_yaml_error_names_the_offending_field():
    """A schema error has to say what is wrong with the file.

    The pydantic ValidationError is caught and replaced with "Could not
    validate file X", discarding the one piece of information the user needs.
    Pydantic already knows the field is misspelled; it just never gets shown.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        bad = Path(work_dir) / "bad.yaml"
        bad.write_text(TYPO_NOTE)

        result = run_brassy([bad, "-d", "2024-10-14"])

        assert result.returncode != 0
        assert "titel" in output_of(result), (
            "the error did not mention the field that failed validation"
        )

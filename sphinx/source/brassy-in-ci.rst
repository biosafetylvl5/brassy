Release Notes Checker
=====================

This GitHub Action checks release notes in your repo.
It ensures that contributors properly document changes by
checking for the presence of new release note files.
It also protects your old release notes by preventing
modifications to existing rst release notes.

Usage
-----

Create a workflow file that uses this reusable action:

.. code-block:: yaml

    name: Has correct release note edits

    on:
      push:
        branches: 'main'
      pull_request:

    jobs:
      check-release-notes:
        uses: biosafetylvl5/brassy/.github/workflows/reusable-check-release-notes.yaml@main # you should specify a
        commit here
        with:
          release_notes_dir: 'sphinx/source/releases'
          latest_notes_dir: 'sphinx/source/releases/latest'
          check_rst_files: true
          check_yaml_files: true
          allow_rst_edits: false
          require_yaml_changes: true
          skip_on_release_branch: true
          file_extensions: 'rst,yaml,yml'
          release_branch_pattern: '^(release/v[0-9]+\.[0-9]+\.[0-9]+|hotfix/.+)$'

Configuration Options
---------------------

Paths and Directories
^^^^^^^^^^^^^^^^^^^^^

- **``release_notes_dir``**: Directory containing all release notes (default: ``docs/source/releases``)
- **``latest_notes_dir``**: Directory containing release notes for the current development cycle (default:
  ``docs/source/releases/latest``)

File Type Controls
^^^^^^^^^^^^^^^^^^

- **``check_rst_files``**: Whether to check for changes to RST files (default: ``true``)
- **``check_yaml_files``**: Whether to check for changes to YAML files (default: ``true``)
- **``file_extensions``**: Comma-separated list of file extensions to check (default: ``rst,yaml``)

Behavior Controls
^^^^^^^^^^^^^^^^^

- **``allow_rst_edits``**: Whether to allow direct edits to RST files (default: ``false``)
- **``require_yaml_changes``**: Whether to require new/modified YAML release notes (default: ``true``)
- **``skip_on_release_branch``**: Whether to skip checks on release branches (default: ``true``)
- **``release_branch_pattern``**: Regex pattern to identify release branches (default:
  ``^release/v[0-9]+\.[0-9]+\.[0-9]+$``)

Outputs
^^^^^^^

The action provides the following outputs that can be used in subsequent workflow steps:

- **``rst_changes_detected``**: ``true`` if RST file changes were detected
- **``yaml_changes_detected``**: ``true`` if YAML file changes were detected
- **``is_release_branch``**: ``true`` if the current branch matches the release branch pattern

Use Cases
---------

Standard PR Validation
^^^^^^^^^^^^^^^^^^^^^^

Ensure every PR that _should_ include release notes, _does_ include release notes:

.. code-block:: yaml

       with:
         require_yaml_changes: true

Custom Release Branch Pattern
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your project uses a different naming convention for release branches,
you can edit the "release branch" regex.

The action uses regex patterns to identify release branches. Here are some examples:

- **Default**: ``^release/v[0-9]+\.[0-9]+\.[0-9]+$``

  - Matches: ``release/v1.2.3``, ``release/v10.0.0``
  - Doesn't match: ``feature/new-thing``, ``bugfix/issue-123``

- **Include hotfix branches**: ``^(release/v[0-9]+\.[0-9]+\.[0-9]+|hotfix/.+)$``

  - Matches: ``release/v1.2.3``, ``hotfix/critical-bug``

- **Calendar versioning**: ``^release/[0-9]{4}\.[0-9]{2}$``

  - Matches: ``release/2023.05``, ``release/2024.01``

- **Custom versioning**: ``^(rel-[0-9]{4}-[0-9]{2}|version/[0-9]+)$``

  - Matches: ``rel-2023-05``, ``version/42``

.. code-block:: yaml

       with:
         release_branch_pattern: '^(release/v[0-9]+\.[0-9]+\.[0-9]+|hotfix/.+)$'

Alternatively, set this to blank to disable:

.. code-block:: yaml

       with:
         release_branch_pattern: ''

Allowing RST Edits in Specific Workflows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have a workflow where you need to modify RST release notes files directly,
you can disable the rst edit check:

.. code-block:: yaml

       with:
         allow_rst_edits: true

Checking Custom File Extensions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your project uses different file extensions for release notes:

.. code-block:: yaml

       with:
         file_extensions: 'yaml_file.yet_another_yaml'

Troubleshooting
---------------

No YAML Changes Detected
^^^^^^^^^^^^^^^^^^^^^^^^

If the action fails with "No YAML release note changes detected":

1. Add a new release note file in the ``latest_notes_dir`` directory using brassy
3. Ensure the file has the correct extension (``.yaml`` or ``.yml``)

RST Changes Detected
^^^^^^^^^^^^^^^^^^^^

If the action fails with "Release note RST changes detected":

1. Check that you have not accidentally modified RST release files directly in a branch that isn't a release branch
3. If you need to edit RST files directly, set ``allow_rst_edits: true``

Contributing
------------

Contributions to improve this action are welcome! Please submit a PR with your proposed changes.

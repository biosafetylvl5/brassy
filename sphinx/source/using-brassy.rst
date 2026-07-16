Using Brassy
============

Example usage
-------------

Create YAML template
^^^^^^^^^^^^^^^^^^^^

Brassy can create blank yaml templates for release notes.
By default, brassy will name the file after your current git
branch name. You can also specify a name manually, and
``.yaml`` will be appended if you do not end your file name with
``.yml`` or ``.yaml``. You can do this with the following command:

.. code-block:: bash

    brassy --write-yaml-template release-note.yaml
    # or
    brassy -t release-note.yaml
    # or leave blank to name after current git branch
    brassy -t

By default, the yaml template will be populated with the following fields:

.. runcmd:: python3 -c "from brassy.templates.release_yaml_template import categories; print('\n'.join(categories))"

You can configure this in your ``.brassy`` file. See also Settings.

For example, the section for ``bug-fix`` will look like this:

.. code-block:: yaml

    bug fix:
    - title: ''
      description: |
      files:
        deleted:
        - ''
        moved:
        - ''
        added:
        - ''
        modified:
        - ''
      related-issue:
        number: null
        repo_url: ''
      date:
        start: null
        finish: null

For example:

.. code-block:: yaml

    bug fix:
    - title: 'Fix elephant related crash'
      description: |
            - Fixed a bug where the program would crash when the user thought of elephants.
      description: |
      files:
        deleted:
        - 'die-on-thoughts.py'
        moved:
        - ''
        added:
        - ''
        modified:
        - 'main.py'
      related-issue:
        number: 1938
        repo_url: 'http://github.com/fake/repo'
      date:
        start: "10-10-1999"
        finish: "02-21-2026"

Generating the changed files via ``git``
""""""""""""""""""""""""""""""""""""""""

You can run ``brassy`` with ``--get-changed-files`` (or ``-c``)
to output the files that have been
modified, added, deleted or moved in the current branch as compared to the main
branch. It runs on the current directory by default,
but it accepts a path as an argument.

For example, the output looks like this:

.. code-block:: yaml

    brassy --get-changed-files

        added:
        - test.py
        modified:
        - test2.js
        deleted:
        - test3.cpp
        moved:
        - test4.fortran

It prints with indents for easy copy-and-pasting into your yaml files.

Generate release notes
----------------------

Once you have filled out your yaml template,
you can generate release notes with the following command:

.. code-block:: bash

    brassy --output-file new-release-note.rst release-note.yaml
    brassy -o new-release-note.rst release-note.yaml

For example, if release-note.yaml contains the following:

.. literalinclude :: ./examples/basic-usage/release-note.yaml
   :language: yaml

The output will be:

.. literalinclude :: ./examples/basic-usage/new-release-note
   :language: rst

Specifying Version
^^^^^^^^^^^^^^^^^^

You can specify the version of the release notes by using the
``--release-version`` or ``-r`` flag.

For example, using the previous yaml file:

.. code-block:: bash

    brassy -o new-release-note.rst release-note.yaml -r 1.0.0

Which would output:

.. literalinclude :: ./examples/basic-usage/new-release-note-v1
   :language: rst

Specifying Date
^^^^^^^^^^^^^^^

By default, brassy uses todays date in ``YYYY-MM-DD`` format.

You can specify the date of the release notes in any format
with the ``-d`` or ``--release-date`` flag.

For example, using the previous yaml file:

.. code-block:: bash

    brassy -o new-release-note.rst release-note.yaml -d 3000-30-30

Which would output:

.. literalinclude :: ./examples/basic-usage/new-release-note-date
   :language: rst

Adding Headers and/or Footers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can add headers and/or footers to your release notes by using the
``-p`` or ``--prefix-file`` and ``-s`` or ``--suffix-file`` flags.

For example, for the following files:

``header.txt``
    .. literalinclude :: ./examples/basic-usage/header.txt
``footer.txt``
    .. literalinclude :: ./examples/basic-usage/footer.txt

Using the previous yaml file,

.. code-block:: bash

    brassy -o new-release-note.rst release-note.yaml -p header.txt -s footer.txt

Would output:

.. literalinclude :: ./examples/basic-usage/new-release-note-header-footer

Customizing Output Templates
----------------------------

Brassy uses an internal template to control how release notes are rendered.
The default template produces standard RST output with a version title, a
summary list, and detailed sections for each change category. You can
override this template in your ``.brassy`` configuration file.

The template consists of five named sections that are rendered in order:

``header``
    Prepended before the release title. Contains ``{prefix_file}`` which
    is replaced with the contents of the file passed via ``--prefix-file``.

``title``
    The release version heading (e.g. "Version 1.0.0 (2024-10-14)").

``summary``
    A bullet list of changes, one line per entry. This section is rendered
    once per entry and is intended to repeat.

``entry``
    The detailed change descriptions. This section is split into two parts:
    **category-level lines** (rendered once per category) and **entry-level
    lines** (rendered once per entry). The split occurs at the first line
    containing ``{title}``, ``{description}``, or ``{file_change}``.

``footer``
    Appended after all entries. Contains ``{suffix_file}`` which is replaced
    with the contents of the file passed via ``--suffix-file``.

Available template variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+---------------------------+---------------------------------------------+
| Variable                  | Replaced with                               |
+===========================+=============================================+
| ``{change_type}``         | Capitalized category name (e.g. "Bug fix")  |
+---------------------------+---------------------------------------------+
| ``{title}``               | The change entry title                      |
+---------------------------+---------------------------------------------+
| ``{description}``         | The change entry description                |
+---------------------------+---------------------------------------------+
| ``{file_change}``         | File change type (added, deleted, etc.)     |
+---------------------------+---------------------------------------------+
| ``{file}``                | The file path                               |
+---------------------------+---------------------------------------------+
| ``{prefix_file}``         | Header file content                         |
+---------------------------+---------------------------------------------+
| ``{suffix_file}``         | Footer file content                         |
+---------------------------+---------------------------------------------+
| ``{release_version}``     | Release version string                      |
+---------------------------+---------------------------------------------+
| ``{release_date}``        | Release date string                         |
+---------------------------+---------------------------------------------+

Default template
^^^^^^^^^^^^^^^^

Here is the default template. It is shown with annotations marking which lines
are category-level and which are entry-level in the ``entry`` section:

.. code-block:: yaml

    templates:
      release-template:
        - header:
          - "{prefix_file}"
          - ""
        - title:
          - ""
          - "Version {release_version} ({release_date})"
          - "**************************"
          - ""
        - summary:
          - " * *{change_type}*: {title}"
        - entry:
          - ""                   # category heading (once per category)
          - "{change_type}"      # category heading
          - "==========="        # category heading
          - ""                   # category heading
          - "{title}"            # entry content (per entry)
          - "-------------------------"
          - ""
          - "{description}"
          - ""
          - "::"
          - ""
          - "     {file_change}: {file}"
        - footer:
          - ""
          - "{suffix_file}"

.. note::

   The ``{file}`` variable must appear on a line that also contains
   ``{file_change}`` (or another entry-level variable) to be treated
   as entry-level. Please do not use ``{file}`` without
   ``{file_change}`` in custom templates.

.. warning::

   Template customization is an alpha feature. The schema and rendering
   logic may change in future releases without backward compatibility.

Related Issue
-------------

Brassy can link issues (aka tasks, bugs, cards, etc.) to changes.

For example:

.. code-block:: yaml

  continuous integration:
  - title: 'Delete repo upon push'
    description: 'I am done coding. Just delete the repo.'
    files:
      deleted:
      - 'main.py'
      added:
      - 'delete-everything.py'
    related-issue:
      number: 999
      repo_url: 'https://github.com/torvalds/linux'

links the change "Delete repo upon push" to issue #999 on the linked linux repo.

.. warning::

  Issue information isn't rendered in generated release notes by default.
  You must (currently) change your release generation template to include
  issue info in your release notes.

Support for Internal Repos
^^^^^^^^^^^^^^^^^^^^^^^^^^

Some repositories aren't something you can share a link for.
For example, they might be on an internal server or on your
personal laptop.

In these cases, you can specify issues without a URL. They must follow this pattern:

.. code-block::

  Repo Name Or Other String#999 - Description or other string

For example:

.. code-block:: yaml

  related-issue:
    internal: "Brassy#0 - Fake issue as an example for change"

Change YAML directory
---------------------

By default brassy works in your current working directory.

You can specify a directory with ``--yaml-dir`` or ``-yd``.

For example:

.. code-block:: bash

    brassy --yaml-dir ./docs/release-notes/v1.0.0 \
           --write-template "updating-gpu-code"

would write a template file ``updating-gpu-code.yaml``
to ``./docs/release-notes/v1.0.0``.

Prune YAML file
---------------

Brassy can "prune" yaml files by removing blank sections. Sections are considered blank
if all of their items are blank OR are empty lists.

For example:

.. literalinclude :: ./examples/basic-usage/to-prune.yaml

would become

.. literalinclude :: ./examples/basic-usage/pruned.yaml

after pruning.

To prune a file, pass it to brassy with ``--prune``.
Eg. ``brassy --prune fake_file.yaml``

Controlling CLI Output
----------------------

You can turn off fancy formatting (colors, bold, etc.)
by using the ``--no-color``/``-nc`` flag.

You can also turn off all non-error outputs by using the ``--quiet`` or ``-q`` flag.

Help!
-----

When in doubt, you can always run the help command to see what options are available:

.. code-block:: bash

    brassy --help

Which outputs:

.. runcmd:: brassy --help

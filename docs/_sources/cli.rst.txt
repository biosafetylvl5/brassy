CLI
===

Example usage
-------------

Create YAML template
^^^^^^^^^^^^^^^^^^^^

Yarn can create blank yaml templates for release notes. By default, yarn will name the file after your current git
branch name. You can also specify a name manually, and ``.yaml`` will be appended if you do not end your file name with
``.yml`` or ``.yaml``. You can do this with the following command:

.. code-block:: bash

    yarn --write-yaml-template release-note.yaml

By default, the yaml template will be populated with the following fields:

.. runcmd:: python3 -c "from yarn import yarn; print('\n'.join(yarn.default_categories))"

For example, the section for ``bug-fix`` will look like this:

.. code-block:: yaml

    bug-fix:
      - title: ""
        description: ""

Generate release notes
^^^^^^^^^^^^^^^^^^^^^^

Once you have filled out your yaml template, you can generate release notes with the following command:

.. code-block:: bash

    yarn -o new-release-note.rst release-note.yaml

For example, if release-note.yaml contains the following:

.. literalinclude :: ./examples/basic-usage/release-note.yaml
   :language: yaml

The output will be:

.. literalinclude :: ./examples/basic-usage/new-release-note
   :language: rst

Specifying Version
^^^^^^^^^^^^^^^^^^

You can specify the version of the release notes by using the ``-v`` or ``--version`` flag.
For example, using the previous yaml file:

.. code-block:: bash

    yarn -o new-release-note.rst release-note.yaml -v 1.0.0

Which would output:

.. literalinclude :: ./examples/basic-usage/new-release-note-v1
   :language: rst

Specifying Date
^^^^^^^^^^^^^^^

You can specify the date of the release notes by using the ``-d`` or ``--release-date`` flag.

For example, using the previous yaml file:

.. code-block:: bash

    yarn -o new-release-note.rst release-note.yaml -d 3000-30-30

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

    yarn -o new-release-note.rst release-note.yaml -p header.txt -s footer.txt

Would output:

.. literalinclude :: ./examples/basic-usage/new-release-note-header-footer

Controlling CLI Output
^^^^^^^^^^^^^^^^^^^^^^

You can turn off fancy formatting (colors, bold, etc.) by using the ``--no-color``/``-nc`` flag.

You can also turn off ALL non-error outputs by using the ``--quiet``/``-q`` flag.

Help!
^^^^^

When in doubt, you can always run the help command to see what options are available:

.. code-block:: bash

    yarn --help

Which outputs:

.. runcmd:: yarn --help

Arguments
---------

.. argparse::
    :filename: ../yarn/yarn.py
    :func: get_parser

Version [UNKNOWN] (2024-10-15)
**************************

 * *Bug fix*: Print pretty error on blank yaml.
 * *Bug fix*: Fix empty "--write-yaml-template bug
 * *Bug fix*: Fix bug with --write-template-error
 * *Bug fix*: Make optional dates optional
 * *Enhancement*: Add internal option to related issue
 * *Enhancement*: Add start and finish dates for changes
 * *Enhancement*: Put title at top of template
 * *Documentation*: Fix docs rendering of examples.
 * *Continuous integration*: Add integration tests

Bug fix
===========

Print pretty error on blank yaml.
-------------------------

Now prints "no valid yaml content in file. please populate example.yaml" when run on blank yaml file.

::

     modified: src/brassy/brassy.py

Bug fix
===========

Fix empty "--write-yaml-template bug
-------------------------

This was previously hotfixed, merging into main codebase now.

::

     modified: src/brassy/brassy.py

Bug fix
===========

Fix bug with --write-template-error
-------------------------

Fixed issue where --write-template-error wouldnt run without argument

::

     modified: src/brassy/brassy.py

Bug fix
===========

Make optional dates optional
-------------------------

Dates for changes are optional. this fix allows users to leave the entry off,
rather than requiring a null field for building.


::

     modified: src/brassy/templates/release_yaml_template.py

Enhancement
===========

Add internal option to related issue
-------------------------

Some organizations use internal repos that cannot be accessed by ci. this change adds an "internal" field for the related issue so that users can add strings directly rather than use the url+issue number combo previously provided. the strings are rendered directly, but must fit a "repo#number - description" pattern. the field is named "internal" to suggest to users that when possible the url option *should* be used to access future functionality.

::

     modified: src/brassy/templates/release_yaml_template.py

Enhancement
===========

Add start and finish dates for changes
-------------------------

Per user request, start and finish date fields have been added to the yaml template. they are not rendered yet.

::

     modified: src/brassy/brassy.py

Enhancement
===========

Put title at top of template
-------------------------

Title is now at top of template because users were mixing up description and title. this change is backwards compatible, and no updates to yaml files are needed.

::

     modified: src/brassy/brassy.py

Documentation
===========

Fix docs rendering of examples.
-------------------------

Fix docs rendering of yaml examples by updating old yaml files.

::

     modified: docs/api.html
     modified: docs/genindex.html
     modified: docs/getting-started.html
     modified: docs/index.html
     modified: docs/objects.inv
     modified: docs/searchindex.js
     modified: pyproject.toml
     modified: sphinx/source/examples/basic-usage/new-release-note
     modified: sphinx/source/examples/basic-usage/new-release-note-date
     modified: sphinx/source/examples/basic-usage/new-release-note-header-footer
     modified: sphinx/source/examples/basic-usage/new-release-note-v1
     modified: sphinx/source/examples/basic-usage/release-note.yaml
     deleted: docs/py-modindex.html

Continuous integration
===========

Add integration tests
-------------------------

Added basic integration tests. more work needed.


::

     added: pytest.ini
     added: tests/inputs/barebones.yaml
     added: tests/inputs/fully-featured.yaml
     added: tests/inputs/mostly-featured.yaml
     added: tests/inputs/to-prune.yaml
     added: tests/outputs/barebones.rst
     added: tests/outputs/fully-featured.rst
     added: tests/outputs/mostly-featured.rst
     added: tests/outputs/pruned.yaml
     added: tests/test_integ.py
     deleted: test/575-cli-class-factory.yaml
     deleted: test/burgers.rst
     deleted: test/burgers.yaml
     deleted: test/test.py
     deleted: test/test.rst
     deleted: test/test2.yaml
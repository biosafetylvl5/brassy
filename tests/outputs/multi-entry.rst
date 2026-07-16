Version [UNKNOWN] (2024-10-14)
**************************

 * *Bug fix*: Fixed crash on app startup
 * *Bug fix*: Fixed off-by-one in parser
 * *Enhancement*: Added dark mode
 * *Enhancement*: Added export to json

Bug fix
===========

Fixed crash on app startup
-------------------------

The app no longer crashes when started with no arguments.


`#100 <https://github.com/example/repo/issues/100>`_

::

     modified: src/startup.py

Fixed off-by-one in parser
-------------------------

Loop bound corrected in the YAML parser.


`#101 <https://github.com/example/repo/issues/101>`_

::

     modified: src/parser.py

Enhancement
===========

Added dark mode
-------------------------

Users can now switch to a dark color scheme.


`#200 <https://github.com/example/repo/issues/200>`_

::

     added: src/themes/dark.py
     modified: src/main.py

Added export to json
-------------------------

Release notes can now be exported in JSON format.


`#201 <https://github.com/example/repo/issues/201>`_

::

     added: src/export/json.py
     modified: src/export/__init__.py
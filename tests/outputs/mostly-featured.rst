Version [UNKNOWN] (2024-10-14)
**************************

 * *Bug fix*: Fixed bubble blowing glitch
 * *Enhancement*: Added krabby patty secret formula encryption
 * *Deprecation*: Deprecated old jellyfish net api
 * *Removal*: Removed rock bottom map support
 * *Performance*: Optimized patricks rock loading time
 * *Documentation*: Updated mermaid man and barnacle boy mission logs
 * *Continuous integration*: Implemented jellyfish fields ci/cd pipeline

Bug fix
===========

Fixed bubble blowing glitch
-------------------------

Resolved an issue where bubble shapes would not form correctly when using the Bubble Blowing Wand.


`#101 <https://github.com/spongebob-app/bubble-wand/issues/101>`_

::

     modified: src/bubble_wand.py

Enhancement
===========

Added krabby patty secret formula encryption
-------------------------

Implemented advanced encryption for the Krabby Patty secret formula to enhance security.


`#202 <https://github.com/spongebob-app/krusty-krab/issues/202>`_

::

     added: src/secret_formula_encryption.py
     modified: src/krusty_krab_menu.py

Deprecation
===========

Deprecated old jellyfish net api
-------------------------

The old Jellyfish Net API is now deprecated in favor of the new Electric Jellyfish Net API.


`#303 <https://github.com/spongebob-app/jellyfish-net/issues/303>`_

::

     modified: src/jellyfish_net_v1.py

Removal
===========

Removed rock bottom map support
-------------------------

Dropped support for the Rock Bottom map due to low user engagement and maintenance overhead.


`#404 <https://github.com/spongebob-app/maps/issues/404>`_

::

     deleted: maps/rock_bottom_map.py
     modified: src/map_loader.py

Performance
===========

Optimized patricks rock loading time
-------------------------

Improved the loading time for Patrick's Rock environment by 60% through asset optimization.


`#505 <https://github.com/spongebob-app/environments/issues/505>`_

::

     modified: assets/patricks_rock/*

Documentation
===========

Updated mermaid man and barnacle boy mission logs
-------------------------

Added new entries and corrected errors in the mission logs for better clarity and accuracy.


`#606 <https://github.com/spongebob-app/docs/issues/606>`_

::

     added: docs/mission_logs/mission_99.md
     modified: docs/mission_logs/index.md

Continuous integration
===========

Implemented jellyfish fields ci/cd pipeline
-------------------------

Set up CI/CD pipeline using Jenkins for automated testing and deployment of the Jellyfish Fields module.


`#707 <https://github.com/spongebob-app/ci/issues/707>`_

::

     added: ci/jenkinsfile
     modified: ci/config.yml
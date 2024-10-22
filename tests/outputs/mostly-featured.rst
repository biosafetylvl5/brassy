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


::

     modified: src/bubble_wand.py

Enhancement
===========

Added krabby patty secret formula encryption
-------------------------

Implemented advanced encryption for the Krabby Patty secret formula to enhance security.


::

     added: src/secret_formula_encryption.py
     modified: src/krusty_krab_menu.py

Deprecation
===========

Deprecated old jellyfish net api
-------------------------

The old Jellyfish Net API is now deprecated in favor of the new Electric Jellyfish Net API.


::

     modified: src/jellyfish_net_v1.py

Removal
===========

Removed rock bottom map support
-------------------------

Dropped support for the Rock Bottom map due to low user engagement and maintenance overhead.


::

     deleted: maps/rock_bottom_map.py
     modified: src/map_loader.py

Performance
===========

Optimized patricks rock loading time
-------------------------

Improved the loading time for Patrick's Rock environment by 60% through asset optimization.


::

     modified: assets/patricks_rock/*

Documentation
===========

Updated mermaid man and barnacle boy mission logs
-------------------------

Added new entries and corrected errors in the mission logs for better clarity and accuracy.


::

     added: docs/mission_logs/mission_99.md
     modified: docs/mission_logs/index.md

Continuous integration
===========

Implemented jellyfish fields ci/cd pipeline
-------------------------

Set up CI/CD pipeline using Jenkins for automated testing and deployment of the Jellyfish Fields module.


::

     added: ci/jenkinsfile
     modified: ci/config.yml
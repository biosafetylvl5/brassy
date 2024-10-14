Version [UNKNOWN] (2024-10-14)
******************************

 * *Bug fix*: Fixed Bubble Blowing Glitch
 * *Enhancement*: Added Krabby Patty Secret Formula Encryption
 * *Deprecation*: Deprecated Old Jellyfish Net API
 * *Removal*: Removed Rock Bottom Map Support
 * *Performance*: Optimized Patricks Rock Loading Time
 * *Documentation*: Updated Mermaid Man and Barnacle Boy Mission Logs
 * *Continuous integration*: Implemented Jellyfish Fields CI/CD Pipeline

Bug fix
=======

Fixed Bubble Blowing Glitch
---------------------------

Resolved an issue where bubble shapes would not form correctly when using the Bubble Blowing Wand.


::

    modified: src/bubble_wand.py

Enhancement
===========

Added Krabby Patty Secret Formula Encryption
--------------------------------------------

Implemented advanced encryption for the Krabby Patty secret formula to enhance security.


::

    added: src/secret_formula_encryption.py
    modified: src/krusty_krab_menu.py

Deprecation
===========

Deprecated Old Jellyfish Net API
--------------------------------

The old Jellyfish Net API is now deprecated in favor of the new Electric Jellyfish Net API.


::

    modified: src/jellyfish_net_v1.py

Removal
=======

Removed Rock Bottom Map Support
-------------------------------

Dropped support for the Rock Bottom map due to low user engagement and maintenance overhead.


::

    deleted: maps/rock_bottom_map.py
    modified: src/map_loader.py

Performance
===========

Optimized Patricks Rock Loading Time
------------------------------------

Improved the loading time for Patrick's Rock environment by 60% through asset optimization.


::

    modified: assets/patricks_rock/*

Documentation
=============

Updated Mermaid Man and Barnacle Boy Mission Logs
-------------------------------------------------

Added new entries and corrected errors in the mission logs for better clarity and accuracy.


::

    added: docs/mission_logs/mission_99.md
    modified: docs/mission_logs/index.md

Continuous integration
======================

Implemented Jellyfish Fields CI/CD Pipeline
-------------------------------------------

Set up CI/CD pipeline using Jenkins for automated testing and deployment of the Jellyfish Fields module.


::

    added: ci/jenkinsfile
    modified: ci/config.yml

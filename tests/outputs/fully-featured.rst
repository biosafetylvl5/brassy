Version [UNKNOWN] (2024-10-14)
******************************

 * *Bug fix*: Fixed Aang's Avatar State Ⓐ
 * *Enhancement*: Implemented Multi-Element Bending for Avatars
 * *Deprecation*: Deprecated Old Bending Stances
 * *Removal*: Removed Unagi Sea Serpent from Kyoshi Island
 * *Performance*: Optimized Fire Nation Ship Rendering
 * *Documentation*: Added Documentation for Combustion Bending
 * *Continuous integration*: Implemented Nightly Builds for the Fire Nation Branch

Bug fix
=======

Fixed Aang's Avatar State Ⓐ
---------------------------

Resolved an issue where Aang could not exit the Avatar State after consuming cactus juice. This caused unintended behavior and prevented progression in the story.


::

    moved: src/characters/aang_temp.py:src/characters/aang.py
    modified: src/avatar/avatar_state_manager.py

Enhancement
===========

Implemented Multi-Element Bending for Avatars
---------------------------------------------

Avatars can now bend multiple elements simultaneously, allowing for more complex combat strategies.


::

    added: src/bending/multi_element.py

Deprecation
===========

Deprecated Old Bending Stances
------------------------------

The classic bending stances are deprecated in favor of dynamic stances that adapt to the situation.


::

    modified: assets/animations/stances/*

Removal
=======

Removed Unagi Sea Serpent from Kyoshi Island
--------------------------------------------

The Unagi has been removed due to community feedback regarding difficulty levels.


::

    deleted: assets/creatures/unagi.obj
    deleted: src/creatures/unagi_behavior.py

Performance
===========

Optimized Fire Nation Ship Rendering
------------------------------------

Improved rendering performance for Fire Nation ships by 50% by reducing polygon count and optimizing textures.


::

    modified: assets/vehicles/fire_nation_ship.obj

Documentation
=============

Added Documentation for Combustion Bending
------------------------------------------

New documentation explains the mechanics and limitations of combustion bending.


::

    added: docs/bending/combustion_bending.md

Continuous integration
======================

Implemented Nightly Builds for the Fire Nation Branch
-----------------------------------------------------

Set up nightly builds and tests for the Fire Nation development branch to ensure stability.


::

    added: .github/workflows/nightly_fire_nation.yml

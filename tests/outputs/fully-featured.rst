Version [UNKNOWN] (2024-10-14)
**************************

 * *Bug fix*: Fixed aang's avatar state ⓐ
 * *Enhancement*: Implemented multi-element bending for avatars
 * *Deprecation*: Deprecated old bending stances
 * *Removal*: Removed unagi sea serpent from kyoshi island
 * *Performance*: Optimized fire nation ship rendering
 * *Documentation*: Added documentation for combustion bending
 * *Continuous integration*: Implemented nightly builds for the fire nation branch

Bug fix
===========

Fixed aang's avatar state ⓐ
-------------------------

Resolved an issue where Aang could not exit the Avatar State after consuming cactus juice. This caused unintended behavior and prevented progression in the story.


::

     moved: src/characters/aang_temp.py:src/characters/aang.py
     modified: src/avatar/avatar_state_manager.py

Enhancement
===========

Implemented multi-element bending for avatars
-------------------------

Avatars can now bend multiple elements simultaneously, allowing for more complex combat strategies.


::

     added: src/bending/multi_element.py

Deprecation
===========

Deprecated old bending stances
-------------------------

The classic bending stances are deprecated in favor of dynamic stances that adapt to the situation.


::

     moved: assets/animations/stances/*
     moved: tests/unit_tests/{pydantic => models/v1}/sectors/test_cases.yaml

Removal
===========

Removed unagi sea serpent from kyoshi island
-------------------------

The Unagi has been removed due to community feedback regarding difficulty levels.


::

     deleted: assets/creatures/unagi.obj
     deleted: src/creatures/unagi_behavior.py

Performance
===========

Optimized fire nation ship rendering
-------------------------

Improved rendering performance for Fire Nation ships by 50% by reducing polygon count and optimizing textures.


::

     modified: assets/vehicles/fire_nation_ship.obj

Documentation
===========

Added documentation for combustion bending
-------------------------

New documentation explains the mechanics and limitations of combustion bending.


::

     added: docs/bending/combustion_bending.md

Continuous integration
===========

Implemented nightly builds for the fire nation branch
-------------------------

Set up nightly builds and tests for the Fire Nation development branch to ensure stability.


::

     added: .github/workflows/nightly_fire_nation.yml
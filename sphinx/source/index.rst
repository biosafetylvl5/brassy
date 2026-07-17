.. brassy documentation master file, created by
   sphinx-quickstart on Fri Jun 21 11:21:05 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to brassy's documentation!
==================================

**brassy** (Build Release Assembler for Sane Software with YAML) builds release
notes from small, per-change YAML files instead of one shared changelog. Each
contributor adds a YAML note describing their change -- title, description,
files touched, and an optional related issue -- alongside their pull request,
so there is no single changelog file for everyone to merge-conflict over.
When it's time to cut a release, brassy reads every note and renders them into
a single formatted RST document.

Install it with:

.. code-block:: bash

    pip install brassy

Then see :doc:`using-brassy` to get started, or :doc:`brassy-in-ci` to enforce
that every pull request adds a release note.

.. toctree::
   :maxdepth: 2

   using-brassy
   brassy-in-ci
   api
   ./releases/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

`GitHub Repository <https://github.com/biosafetylvl5/brassy>`_

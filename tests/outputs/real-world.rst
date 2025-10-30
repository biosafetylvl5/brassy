Version [UNKNOWN] (2024-10-14)
**************************

 * *Performance*: Deduplicate and centralize variable_name lookup in xarray_obj across coverage checkers

Performance
===========

Deduplicate and centralize variable_name lookup in xarray_obj across coverage checkers
-------------------------

Removes redundant variable_name lookup logic and centralizes it in the relevant model validator

::

     added: docs/source/releases/latest/1182-centralize-variable-name-lookup-in-xarray-obj-coverage-checkers.yaml
     modified: geoips/plugins/modules/coverage_checkers/center_radius.py
     modified: geoips/plugins/modules/coverage_checkers/center_radius_rgb.py
     modified: geoips/plugins/modules/coverage_checkers/masked_arrays.py
     modified: geoips/plugins/modules/coverage_checkers/numpy_arrays_nan.py
     modified: geoips/plugins/modules/coverage_checkers/rgb.py
     modified: geoips/plugins/modules/coverage_checkers/windbarbs.py
     modified: geoips/pydantic_models/v1/coverage_checkers.py
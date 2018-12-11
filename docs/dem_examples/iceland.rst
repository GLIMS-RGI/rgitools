Dyngjujoekull (Iceland)
=======================

Located in Iceland (`64°43'03"N 17°03'28"W <https://goo.gl/maps/2cZCQwY1kx22>`_).

The sources available are: DEM3, ASTER, TanDEM-X, ArcticDEM. **The current
default is DEM3**.

Summary
-------

- ASTER is very bad. The artefacts are not flagged as missing data like it
  mostly is in TanDEM-X or ArcticDEM
- TanDEM-X and ArcticDEM agree well
- DEM3 was generated before these new products, so I guess that a little bit
  of magic was needed to generate the map

Maps
----

.. image:: /_static/dems_examples/iceland/dem_topo_color.png
    :width: 100%

Shaded relief
-------------

.. image:: /_static/dems_examples/iceland/dem_topo_shade.png
    :width: 100%


Differences
-----------

.. image:: /_static/dems_examples/iceland/dem_diffs.png
    :width: 100%



Scatter plots
-------------

These scatter plots are for the glacier area only.

.. image:: /_static/dems_examples/iceland/dem_scatter.png
    :width: 100%

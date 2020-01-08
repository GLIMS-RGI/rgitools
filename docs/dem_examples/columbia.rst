Columbia (Alaska)
=================

Located in Alaska (`61°12'02"N 146°54'17"W <https://goo.gl/maps/WSLkyYAKqd72>`_),
RGI60-01.10689.

The sources available are: ASTER, AW3D30, DEM3, ArcticDEM, TanDEM-X and MAPZEN.
**The current default is DEM3**.

Summary
-------

- ASTER (when it has no gaps, which is the case here) is noisy over flat
  glacier surfaces (north-east of the glacier)
- DEM3 is obviously based on ASTER but is smoother
- clear differences between ASTER and the newer products (TanDEM-X,
  ArcticDEM) might be due to mass-loss, although it seems exaggerated
- it is one of the cases where ArctiDEM has too many data gaps
- AW3D30 also hast way to many gaps


Maps
----

.. image:: /_static/dems_examples/columbia/dem_topo_color.png
    :width: 100%

Shaded relief
-------------

.. image:: /_static/dems_examples/columbia/dem_topo_shade.png
    :width: 100%


Differences
-----------

.. image:: /_static/dems_examples/columbia/dem_diffs.png
    :width: 100%



Scatter plots
-------------

These scatter plots are for the glacier area only.

.. image:: /_static/dems_examples/columbia/dem_scatter.png
    :width: 100%

Gillock Island (Antarctica)
===========================

Located at the East Antarctica (`70°26'06.0"S 71°48'25.3"E <https://goo.gl/maps/XBV3Av6fsBb7ow3A6>`_),
RGI60-19.01251).

The sources available are: ASTER, COPDEM30, COPDEM90, DEM3, RAMP, REMA, MAPZEN and TanDEM-X.

Summary
-------

- ASTER shows ocean
- DEM3 is obviously taken from RAMP
- REMA and TanDEM-X agree quite well
- REMA has small missing featuers
- One of the rare cases where there is no MAPZEN data

Maps
----

.. image:: /_static/dems_examples/gillock/dem_topo_color.png
    :width: 100%

Shaded relief
-------------

.. image:: /_static/dems_examples/gillock/dem_topo_shade.png
    :width: 100%


Differences
-----------

.. image:: /_static/dems_examples/gillock/dem_diffs.png
    :width: 100%



Scatter plots
-------------

These scatter plots are for the glacier area only.
The plots do not work in that case, as MAPZEN DEM only contains NaN values.

.. image:: /_static/dems_examples/gillock/dem_scatter.png
    :width: 100%

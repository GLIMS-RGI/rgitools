.. _dems:

The DEM problem
===============

One of the main goal of rgitools is to provide non only hypsometry but also
local topography maps for each glacier in the RGI.

Unfortunately, **there is no gap-free and freely available global DEM to
date**. For most regions we can rely on a number of sources, which all have
their own issues. Here is the list currently supported by OGGM/rgitools:

- the `Shuttle Radar Topography Mission`_ (SRTM) 90m Digital Elevation Database v4.1
  freely available for all locations in the [60°S; 60°N] range
- the `Greenland Mapping Project`_ (GIMP) Digital Elevation Model
  covering Greenland (RGI region 05)
- the `Radarsat Antarctic Mapping Project`_ (RAMP) Digital Elevation Model, Version 2
  covering the Antarctic continent
  (RGI region 19 with the exception of the peripheral islands)
- the `Advanced Spaceborne Thermal Emission and Reflection Radiometer`_ (ASTER GDEM)
  Global Digital Elevation Model Version 2 covering the entire globe.
- the `Viewfinder Panoramas DEM3`_ products, a global DEM based on various of the
  above listed sources, manually merged and corrected.
- the `TanDEM-X 90m`_ DEM, newly released and covering the entire globe.
- the `Arctic DEM`_ newly released in version 7 and covering the northern
  latitudes at various resolutions (we picked 100m for a start).

.. _Shuttle Radar Topography Mission: http://srtm.csi.cgiar.org/
.. _Greenland Mapping Project: https://bpcrc.osu.edu/gdg/data/gimpdem
.. _Radarsat Antarctic Mapping Project: http://nsidc.org/data/nsidc-0082
.. _Viewfinder Panoramas DEM3: http://viewfinderpanoramas.org/dem3.html
.. _Advanced Spaceborne Thermal Emission and Reflection Radiometer: https://asterweb.jpl.nasa.gov/gdem.asp
.. _TanDEM-X 90m: https://geoservice.dlr.de/web/dataguide/tdm90/
.. _Arctic DEM: https://www.pgc.umn.edu/data/arcticdem/

In theory, this should be enough. In practice, none of the solutions above
is satisfying. We quickly summarize our (temporary) results here, but for now
you can have a look at the following examples:

.. toctree::
    :maxdepth: 1

    dem_examples/hef.rst
    dem_examples/oberaletsch.rst
    dem_examples/columbia.rst
    dem_examples/iceland.rst
    dem_examples/greenland.rst
    dem_examples/devon.rst
    dem_examples/shallap.rst


Summary
-------

We have to keep in mind that any kind of inversion or glacier simulation
based on ice-dynamics cannot deal with artefacts. Therefore, robust and
gap-free datasets are much preferred to accuracy. Furthermore, the concurrent
timing of the glacier outline with the DEM is another important criterion,
as shown by the Columbia example.

Altogether, we are confident in SRTM to be the right choice for all latitudes
below 60° N and S.

For everything else, more investigation is needed. DEM3 offers the stability
and timeliness that TanDEM-X and ArcticDEM cannot (yet) offer.

.. _dems:

The DEM problem
===============

One of the main goals of rgitools is to provide not only aggregated
statistics (hypsometry), but also a local topography map
for each single glacier in the RGI.

Unfortunately, **there is no gap-free and freely available global DEM to
date**. For most regions we can rely on a number of sources, which all have
their own issues. Here is the list currently supported by OGGM/rgitools:

- the `Shuttle Radar Topography Mission`_ (SRTM) 90m Digital Elevation Database v4.1
  freely available for all locations in the [60°S; 60°N] range
- the `Greenland Mapping Project`_ (GIMP) Digital Elevation Model
  covering Greenland (for RGI region 05)
- the `Radarsat Antarctic Mapping Project`_ (RAMP) Digital Elevation Model, Version 2
  covering the Antarctic continent
  (for RGI region 19 with the exception of the peripheral islands)
- the `Advanced Spaceborne Thermal Emission and Reflection Radiometer`_ (ASTER)
  ASTER Global Digital Elevation Model (GDEM) Version 3 (ASTGTM) covering the entire globe but
  with consequent artefacts (not tagged as invalid data).
- the `Viewfinder Panoramas DEM3`_ products, a global DEM based on various of the
  above listed sources, manually merged and corrected.
- the `TanDEM-X 90m`_ DEM, newly released and covering the entire globe.
- the `Arctic DEM`_ newly released in version 7 and covering the northern
  latitudes at various resolutions (we picked 100m for a start).
- the `REMA Antarctic DEM`_ newly released and covering the Antarctic
  continent at various resolutions (we picked 100m for a start).
- the `ALOS World 3D - 30mx`_ (AW3D30) global digital surface model from the
  Japanese space agency JAXA.
- the `AWS terrain tiles`_ data hosted on Amazon Web Services and maintained
  by `Mapzen <https://www.mapzen.com>`_. This is a bundle of
  `various data-sources`_ but very flexible in use.


.. _Shuttle Radar Topography Mission: http://srtm.csi.cgiar.org/
.. _Greenland Mapping Project: https://bpcrc.osu.edu/gdg/data/gimpdem
.. _Radarsat Antarctic Mapping Project: http://nsidc.org/data/nsidc-0082
.. _Viewfinder Panoramas DEM3: http://viewfinderpanoramas.org/dem3.html
.. _Advanced Spaceborne Thermal Emission and Reflection Radiometer: https://doi.org/10.5067/ASTER/ASTGTM.003
.. _TanDEM-X 90m: https://geoservice.dlr.de/web/dataguide/tdm90/
.. _Arctic DEM: https://www.pgc.umn.edu/data/arcticdem/
.. _ALOS World 3D - 30mx: https://www.eorc.jaxa.jp/ALOS/en/aw3d30/
.. _AWS terrain tiles: https://registry.opendata.aws/terrain-tiles/
.. _various data-sources: https://github.com/tilezen/joerd/blob/master/docs/data-sources.md
.. _REMA Antarctic DEM: https://www.pgc.umn.edu/data/rema/

In theory, this should be enough data. In practice, none of the solutions above
is 100% satisfying. We didn't do a thorough assesment yet, but you can have a
look at the following examples:

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

We have to keep in mind that any kind of glacier bed estimate inversion or
glacier simulation based on ice-dynamics cannot deal with artefacts.
Therefore, robust and gap-free datasets are much preferred over more
accurate but incomplete DEMS. Furthermore, the concurrent
timing of the glacier outline with the DEM is another important criterion,
as shown by the Columbia example.

Altogether, we are confident in:
- SRTM for all latitudes below 60° N and S
- GIMP for Greenland
- RAMP for Antarctica (but the peripheral Islands are an issue)

For everything else, more investigation is needed. DEM3 offers the stability
and timeliness that TanDEM-X and ArcticDEM cannot offer (yet), and is the
current default in OGGM.

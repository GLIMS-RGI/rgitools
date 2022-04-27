.. _dems:

The RGI-TOPO dataset (beta release)
===================================

RGI-TOPO provides a local topography map for each single glacier in the RGI.

.. image:: /_static/dems_examples/rgitopo_ex.jpg
    :width: 100%

We gathered and processed topography data for each glacier in the RGI V6 and
for each :ref:`dem-data-sources` we are aware of.
These data are released in a **beta version and are provided here
for feedback and testing purposes only**, i.e. they are not (yet) an
official RGI product. In particular, the various topography data
are provided "as is", i.e. without recommendation on which data source to use.
Note also that RGI-TOPO cannot be used for glacier change assessment: its aim is 
to provide a baseline for glacier modelling and other data analysis efforts. 

Please help us to finalize this product! :ref:`dem-how-to-help` will tell you
how.

.. note::

    We will include the final topography and hypsometry data in the next
    official RGI release (V7) scheduled for release by end of 2020.


Data download
-------------

We processed the data at two different resolutions.
The default version is available at `https://cluster.klima.uni-bremen.de/data/gdirs/dems_v1/default/RGI62/b_010/L1/ <https://cluster.klima.uni-bremen.de/data/gdirs/dems_v1/default/RGI62/b_010/L1/>`_.
And a version with higher spatial resolution is available at `https://cluster.klima.uni-bremen.de/data/gdirs/dems_v1/highres/RGI62/b_020/L1/ <https://cluster.klima.uni-bremen.de/data/gdirs/dems_v1/highres/RGI62/b_020/L1/>`_

See :ref:`dem-data-format` for details on file content, processing and resolution.
And carefully read :ref:`dem-how-to-cite` to find information on the original
data sources and how to acknowledge them.

.. _dem-data-sources:

Data sources
------------

For most regions several data sources are available, each with various
acquisition dates and data quality issues.
Until recently there was no **gap-free, global DEM** available.
This might have changed with the release of `Copernicus DEM GLO-90`_ which so
far shows no artifacts and a very good global coverage:
All but 284 RGI v6 glaciers are covered by Copernicus DEM.
Unfortunately 264 of these are located in the
:ref:`RGI region 19: Antarctic and Subantarctic<rgi19>` which accounts for 10%
of this region's total glaciers. These are mostly situated on small islands
which are either not covered by the DEM or the RGI outlines are slightly
misaligned and placed in the ocean. But this needs further investigation.
Another downside is that the acquisition date of Copernicus DEM (2010-2015)
differs from the target year 2000 of the current and the upcoming RGI outlines.

As of today (Mar 27 2020), the data sources supported by OGGM/rgitools are:

- the `Shuttle Radar Topography Mission`_ (SRTM) 90m Digital Elevation Database v4.1
  freely available for all locations in the [60°S; 60°N] range.
  **Date of acquisition: February 2000**
- the `Greenland Mapping Project`_ (GIMP) Digital Elevation Model
  covering Greenland (for RGI region 05).
  **Date of acquisition: February 2003 - October 2009**
- the `Radarsat Antarctic Mapping Project`_ (RAMP) Digital Elevation Model, Version 2
  covering the Antarctic continent
  (for RGI region 19 with the exception of the peripheral islands).
  **Date of acquisition: 1940-1999 (mostly 1980s and 1990s)**
- the `Advanced Spaceborne Thermal Emission and Reflection Radiometer`_ (ASTER)
  ASTER Global Digital Elevation Model (GDEM) Version 3 (ASTGTM) covering the entire globe but
  with consequent artefacts (not tagged as invalid data).
  **Date of acquisition: 2000 - 2013**
- the `Viewfinder Panoramas DEM3`_ products, a global DEM based on various of the
  above listed sources, manually merged and corrected, sometimes from cartographical data.
  **Date of acquisition: variable, depending on original source.**
- the `TanDEM-X 90m`_ DEM, newly released and covering the entire globe.
  **Date of acquisition: December 2010 - January 2015**
- the `Arctic DEM`_ newly released in version 7 and covering the northern
  latitudes at various resolutions (we picked 100m for a start).
  **Date of acquisition: 2007-2018**
- the `REMA Antarctic DEM`_ newly released and covering the Antarctic
  continent at various resolutions (we picked 100m for a start).
  **Date of acquisition: 2009 - 2017 (mostly 2015-2016)**
- the `ALOS World 3D - 30mx`_ (AW3D30) global digital surface model from the
  Japanese space agency JAXA.
  **Date of acquisition: 2006-2011**
- the `AWS terrain tiles`_ data hosted on Amazon Web Services and maintained
  by `Mapzen <https://www.mapzen.com>`_. This is a bundle of
  `various data-sources`_ but very flexible in use.
  **Date of acquisition: variable, depending on original source**
- the `Copernicus DEM GLO-90`_ is a new global DEM based on WorldDEM and void
  filled using ASTER, SRTM, GMTED2010, TerraSAR-X and ALOS World 3D-30m.
  It is a European Space Agency Copernicus product and freely available at a
  3 arc second resolution.
  **Date of acquisition: 2010-2015**
- the `Alaska V3 DEM`_ is a merged DEM product from SRTM, IFSAR DEM, SPOT
  observations of the SPIRIT program and ASTER with a final resolution of 30m.
  The DEM was created for and is provided by `Kienholz et al., 2014`_.
  **Date of acquisition: 2000-2011**
- the `NASADEM`_ is a merged DEM product with 1 arc second resolution and
  available between 60N and 56S. NASADEM is dereived from the original SRTM
  but postprocessed with updated algorithms and newer auxiliary data which were
  not around for the original SRTM processing.
  **Date of acquisition: February 2000**


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
.. _Copernicus DEM GLO-90: https://bit.ly/2T98qqs
.. _`Alaska V3 DEM`: https://www.the-cryosphere.net/8/503/2014/
.. _`Kienholz et al., 2014`: https://www.the-cryosphere.net/8/503/2014/
.. _`NASADEM`: https://lpdaac.usgs.gov/products/nasadem_hgtv001/

Examples
--------

.. toctree::
    :maxdepth: 1

    dem_examples/hef.rst
    dem_examples/oberaletsch.rst
    dem_examples/columbia.rst
    dem_examples/iceland.rst
    dem_examples/greenland.rst
    dem_examples/devon.rst
    dem_examples/shallap.rst
    dem_examples/nordenskjoeld.rst
    dem_examples/alexander.rst
    dem_examples/gillock.rst
    dem_examples/dobbin.rst
    dem_examples/thana.rst
    dem_examples/tellbreen.rst
    dem_examples/nigards.rst
    dem_examples/olivine.rst
    dem_examples/lenin.rst

These graphics and statistics were generated with a freely available
`Jupyter notebook <https://github.com/OGGM/tutorials/blob/master/notebooks/dem_comparison.ipynb>`_.
You can run this notebook online (without any installation) by following
`this link <https://mybinder.org/v2/gh/OGGM/binder/stable?urlpath=git-pull%3Frepo=https://github.com/OGGM/tutorials%26urlpath%3Dlab%252Ftree%252Ftutorials/./notebooks/dem_comparison.ipynb%26branch%3Dstable>`_
(the online server may take a couple of minutes to start).

.. _dem-data-format:

Data format
-----------

The data is sorted into regional folders (one per RGI region). Each tar file
stores 1000 glaciers (`RGI60-01.00.tar` contains glacier IDs from
`RGI60-01.00001` to `RGI60-01.00999`,  `RGI60-01.01.tar` contains glacier IDs
from `RGI60-01.01000` to `RGI60-01.01999`, etc.).

Each glacier data comes in a single folder named after its RGI ID. A glacier
folder contains the following data files:

- `glacier_mask.tif`: a raster mask of the RGI glacier at the same
  resolution than the associated DEMs (geotiff format).
- `outlines.tar.gz`: the RGI vector outlines for this glacier
- `intersects.tar.gz`: the vector lines of the boundaries between this glacier
  and possible neighbors
- `glacier_grid.json`: information about the grid and map projection
- `diagnostics.json`, `log.txt`: files used by OGGM/rgitools (not relevant here)
- **one folder per available DEM source**, containing a `dem.tif` file
  (geotiff format) **and the data source and citation information** in
  `dem_source.txt` (text file).

The topography data is bilinearily interpolated from the DEM source to a
local **tranverse mercator map projection** (similar to the well known UTM,
but with projection parameters centered on the glacier). Most modern GIS packages
are able to read the projection information out of the geotiff files.

The spatial resolution of the target local grid depends on the size of the
glacier. We use a square relation to the glacier size
(:math:`dx=aS^{\frac{1}{2}}`, with S the area of the glacier
in :math:`\text{km}^{2}`). The parameter a is set to 14 in the default
and 7 in the higher resolution data set.
The resulting dx is clipped to minimum of 10m in both versions.
The maximum of dx is clipped to 200m in the
default and 100m in the higher resolution version.

The map size is chosen so that it is larger than the glacier of about 10 grid
points (20 in the higher resolution version to give approximately the same
extents). A future release of the data will also ship with larger map extents.

.. _dem-how-to-cite:

How to cite these data
----------------------

.. warning::

   **IMPORTANT**: RGI-TOPO does NOT generate any new topography data.
   We use freely available data and interpolate it to a local glacier map.
   If you make use of these data for a publication, presentation or website,
   **it is mandatory to refer to the original data provider as given in the
   dem_source.txt file found in each DEM folder.**

   We are very thankful to the institutions providing these data, and we
   ask our users to acknowledge the original contributions according to their
   respective license (sometimes unclear, unfortunately).

RGI-TOPO itself (i.e., the compilation of data) is licensed under a
`CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`_ license, i.e.
you can use, share and adapt it under the conditions stated by the license and
by acknowledging the rgitools contributors as well as the original data
sources (as explained above). The name of the rgitools contributors cannot be
used to endorse any product or result derived from RGI-TOPO without
prior approval.

.. note::

    If you wish to acknowledge the data processing work that was necessary to
    generate these data in a scientific publication, we suggest the
    following citation: "The glacier dem data was processed with the rgitools and
    OGGM software packages (Maussion et al., 2019
    `doi: 10.5194/gmd-12-909-2019 <https://doi.org/10.5194/gmd-12-909-2019>`_)."


.. _dem-how-to-help:

How to provide feedback
-----------------------

Before the official release with the next RGI version, we aim to:

- make sure that we didn't miss any important data source
- ensure that there is no bug in our processing chain, i.e. that the data is
  properly parsed, reprojected, and documented
- decide on the data format which is most suitable for the majority of users
- publish a detailed report about the quality and data availability of each
  data source
- decide on a "standard" data source for each glacier, which will provide
  the reference hypsometry for future RGI versions

Your help on any of these objectives is very welcome! :ref:`dem-contact` us if
you want to provide feedback.

Regarding the choice of the default data source for the RGI, we currently
formulate the following criteria:

1. robust and gap-free datasets are preferred over more accurate or recent but
   incomplete DEMS. Indeed, we have to keep in mind that any kind of glacier
   bed inversion or glacier simulation based on ice-dynamics cannot deal with
   topographical artefacts.
2. the acquisition date of the DEM must be as close as possible to the
   acquisition date of the glacier outline (which is targeted to be around 2000
   in RGI V7).
3. preferably, the DEM source should be the same for neighboring glaciers. This
   implies that ideally, a single DEM source should be chosen at the region or
   sub-region level.

Currently, we are most confident in SRTM for all latitudes between 60° N and S.
Almost gap free, the SRTM data aquisition date is also very concordant with the
target date of the RGI outlines.

For all other regions, more investigation is needed and your feedback is welcome.


Global data availability
------------------------

The following section shows a more detailed analysis of all the above
mentioned DEMs with respect to the different RGI regions.

Table 1 gives a summary for the RGI regions with respect to the different DEMs.
For this and all further analysis a DEM is only attributed as available to a
individual glacier if the glacier centered cutout has less than 10% missing
data points in this DEM. This threshold obviously only covers actual voids in
the DEM source but does not state anything about the quality or accuracy of the
none-void data points.


.. csv-table:: Table 1: Summary of all RGI regions. First column shows total
    number of glaciers per RGI region. The consecutive columns specify the
    availability of particular DEMs for a RGI region in percent of the total
    glaciers per region. Values are not rounded but truncated so 99% could be
    just one missing glacier. Only DEMs with less than 10% missing values are
    considered.
    :file: _static/tables/dem_allrgi_v1.csv


The following barplot shows again the availability of particular DEMs for RGI
region.

.. image:: /_static/images/barplot_allregions_v1.png
    :width: 100%

In the section :ref:`subregions` you can find similar statistics but broken
down into the RGI Subregions.


.. toctree::
    :hidden:
    :maxdepth: 1

    dems_subregions.rst


Code availability
-----------------

These data where generated with `OGGM version 1.2 <https://github.com/OGGM/oggm>`_.
This `tutorial <https://github.com/OGGM/tutorials/blob/master/notebooks/dem_sources.ipynb>`_
(`interactive version <https://mybinder.org/v2/ghhttps://mybinder.org/v2/gh/OGGM/binder/stable?urlpath=git-pull%3Frepo=https://github.com/OGGM/tutorials%26urlpath%3Dlab%252Ftree%252Ftutorials/./notebooks/dem_sources.ipynb%26branch%3Dstable>`_)
documents how to create local
topography maps yourselves.

.. _dem-contact:

Contact
-------

RGI-TOPO authors:
`Matthias Dusch <https://www.uibk.ac.at/acinn/people/matthias-dusch.html.en>`_ and
`Fabien Maussion <https://fabienmaussion.info/>`_.

For feedback, please use the `github issue tracker <https://github.com/GLIMS-RGI/rgitools/issues>`_
(requires a github account) or send us an email.

Acknowledgements
----------------

.. raw:: html

    <a href="https://cryosphericsciences.org" >
    <img src="https://cryosphericsciences.org/wp-content/themes/iacs/img/iugg_logo_complete.png" alt="Image missing" width="49%" />
    </a>
    <a href="https://www.uibk.ac.at/acinn/" >
    <img src="https://www.uibk.ac.at/public-relations/grafik_design/images/logo/download/sublogos/institute-sublogos/atmospheric-and-cryospheric-sciences.png" alt="Image missing" width="49%" />
    </a>

We acknowledge financial support from the
`International Association of Cryospheric Sciences <https://cryosphericsciences.org>`_
(Matthias Dusch) and from the University of Innsbruck (Fabien Maussion).

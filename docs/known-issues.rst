Known issues in RGI V6
======================

This page lists the issues we discovered in RGI V6.


Data files
----------

- The file '01_rgi60_Alaska_hypso.csv' contains RGI IDs which are still labelled
  as RGI50.
- The column ``Zmed`` in the file '19_rgi60_AntarcticSubantarctic.shp' contains
  only missing data
- the file ``08_rgi60_Scandinavia.shp`` is located in a folder wrongly entitled
  ``07_rgi60_Scandinavia`` (the region number is wrong).
- in the `summary file <http://www.glims.org/RGI/rgi60_files/00_rgi60_summary.zip>`_,
  the RGI subregions of Region 08 (Scandinavia) are wrongly named and the
  subregion 08-03 as defined in the technical report is missing.


Undivided glacier complexes
---------------------------

Large, undivided glacier complexes are the major obstacle towards distributed
flowline modelling at the global scale. Here we list the major glacier
complexes that need to be divided.

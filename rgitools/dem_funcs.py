import logging

import numpy as np
import rasterio

from oggm import GlacierDirectory, entity_task

# Module logger
log = logging.getLogger(__name__)


def dem_quality(gdir, demfile):
    """Quality check based on oggm.simple_glacier_masks.

    Parameters
    ----------
    gdir : :py:class:`oggm.GlacierDirectory`
        the glacier in question
    demfile : str
        path to a specific DEM tif-file

    Returns
    -------
    nanpercent : float
        how many grid points are NaN as a fraction of all grid points
    nanpercent_glc : float
        how many grid points are NaN as a fraction of all glaciated grid points
    meanhgt : float
        mean elevation of grid points
    meanhgt_glc : float
        mean elevation of glaciated grid points
    roughness : float
        standard deviation of 2d slope of all grid points
    roughness_glc : float
        standard deviation of 2d slope of all glaciated grid points
    """

    # open tif-file:
    with rasterio.open(demfile, 'r', driver='GTiff') as ds:
        dem = ds.read(1).astype(rasterio.float32)
        nx = ds.width
        ny = ds.height
        dx = ds.transform[0]
    # assert some basics
    assert nx == gdir.grid.nx
    assert ny == gdir.grid.ny
    assert dx == gdir.grid.dx

    # open glacier mask
    with rasterio.open(gdir.get_filepath('glacier_mask'),
                       'r', driver='GTiff') as ds:
        mask = ds.read(1).astype(rasterio.int16)

    # set nodata values to NaN
    min_z = -999.
    dem[dem <= min_z] = np.NaN
    isfinite = np.isfinite(dem)
    isfinite_glc = np.isfinite(dem[np.where(mask)])

    # calculate fraction of NaNs in all and glaciated area
    nanpercent = np.sum(isfinite) / (nx * ny)
    nanpercent_glc = np.sum(isfinite_glc) / mask.sum()

    # calculate mean elevation of all and glaciated area
    meanhgt = np.nanmean(dem)
    meanhgt_glc = np.nanmean(dem[np.where(mask)])

    # calculate roughness of all area
    sy, sx = np.gradient(dem, dx)
    slope = np.arctan(np.sqrt(sy**2 + sx**2))
    roughness = np.nanstd(slope)

    # calculate roughness of glaciated area
    dem_glc = np.where(mask, dem, np.nan)
    sy, sx = np.gradient(dem_glc, dx)
    slope = np.arctan(np.sqrt(sy**2 + sx**2))
    roughness_glc = np.nanstd(slope)

    return (nanpercent, nanpercent_glc, meanhgt, meanhgt_glc, roughness,
            roughness_glc)


@entity_task(log)
def get_dem_area(gdir):
    """Read the glacier_mask.tif and calculated glacier area based on this

    Parameters
    ----------
    gdir : GlacierDirectory
        the glacier in question

    Returns
    -------
    float
        glacier area in km2
    """

    # read dem mask
    with rasterio.open(gdir.get_filepath('glacier_mask'),
                       'r', driver='GTiff') as ds:
        profile = ds.profile
        data = ds.read(1).astype(profile['dtype'])

    # calculate dem_mask size and test against RGI area
    mask_area_km2 = data.sum() * gdir.grid.dx**2 * 1e-6

    return mask_area_km2

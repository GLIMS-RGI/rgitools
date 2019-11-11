import os
import logging
import tarfile

import pandas as pd
import numpy as np
import rasterio

from oggm import utils, GlacierDirectory, entity_task

# Module logger
log = logging.getLogger(__name__)


def dem_quality(gdir, demfile):
    """Quality check based on oggm.simple_glacier_masks.

    Parameters
    ----------
    gdir : :py:class:`oggm.GlacierDirectory`
        where to write the data

    Returns
    -------
    nanpercent : float
        how many grid points are NaN as a fraction of all grid points
    """

    # open tif-file:
    with rasterio.open(demfile, 'r', driver='GTiff') as ds:
        dem = ds.read(1).astype(rasterio.float32)
        nx = ds.width
        ny = ds.height

    # Grid
    assert nx == gdir.grid.nx
    assert ny == gdir.grid.ny

    min_z = -999.
    dem[dem <= min_z] = np.NaN
    isfinite = np.isfinite(dem)

    nanpercent = np.sum(isfinite) / (nx * ny)

    meanhgt = np.nanmean(dem)

    # TODO : use some proper roughness measure. For now just std
    rough = np.nanstd(dem)

    return nanpercent, meanhgt, rough


def gdirs_from_tar_files(path, rgi_region=None):

    gdirs = []
    for regdir in os.listdir(path):

        # only do required rgi_region
        if (rgi_region is not None) and (regdir[-2:] != rgi_region):
            continue

        rdpath = os.path.join(path, regdir)

        for file in os.listdir(rdpath):

            with tarfile.open(os.path.join(rdpath, file), 'r') as tfile:
                for member in tfile:
                    if member.isdir():
                        continue
                    tar_base = os.path.join(rdpath, member.path)
                    gdirs.append(GlacierDirectory(member.name[-21:-7],
                                                  from_tar=tar_base))

    return gdirs


@entity_task(log)
def check_gdir_dems(gdir):
    """

    :param gdir:
    :return:
    """

    # dataframe for results
    df = pd.DataFrame([], index=[gdir.rgi_id]*3, # np.arange(3),
                      columns=['metric'] + utils.DEM_SOURCES)
    df.iloc[0]['metric'] = 'quality'
    df.iloc[1]['metric'] = 'meanhgt'
    df.iloc[2]['metric'] = 'roughness'


    logfile = (os.path.join(gdir.dir, 'log.txt'))

    # read logfile
    lfdf = pd.read_csv(logfile, delimiter=';', header=None,
                       skipinitialspace=True)

    # loop over dems and save existing ones to test
    dem2test = []
    for _, line in lfdf.iterrows():
        if ('DEM SOURCE' in line[1]) and ('SUCCESS' in line[2]):
            rgi = line[1].split(',')[0]
            dem = line[1].split(',')[2]
            dem2test.append(dem)

    # loop over DEMs
    for dem in dem2test:
        demfile = os.path.join(gdir.dir, dem) + '/dem.tif'
        nans, mhgt, rough = dem_quality(gdir, demfile)
        df.loc[df.metric == 'quality', dem] = nans
        df.loc[df.metric == 'meanhgt', dem] = mhgt
        df.loc[df.metric == 'roughness', dem] = rough

    return df

@entity_task(log)
def get_dem_area(gdir):
    """

    :param gdir:
    :return:
    """

    # read dem mask
    with rasterio.open(gdir.get_filepath('dem_mask'),
                       'r', driver='GTiff') as ds:
        profile = ds.profile
        data = ds.read(1).astype(profile['dtype'])

    # calculate dem_mask size and test against RGI area
    mask_area_km2 = data.sum() * gdir.grid.dx**2 * 1e-6

    #np.testing.assert_almost_equal(mask_area_km2,gdir.rgi_area_km2, decimal=1)

    return mask_area_km2

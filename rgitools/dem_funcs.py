import os
import logging
import tarfile

import pandas as pd
import numpy as np
import rasterio

from oggm import utils, GlacierDirectory, entity_task

# Module logger
log = logging.getLogger(__name__)


def dem_quality_check(gdir, demfile, percent_nans=10.0):
    """Quality check based on oggm.simple_glacier_masks.

    Parameters
    ----------
    gdir : :py:class:`oggm.GlacierDirectory`
        where to write the data
    """

    # open tif-file:
    dem_dr = rasterio.open(demfile, 'r', driver='GTiff')
    dem = dem_dr.read(1).astype(rasterio.float32)

    # Grid
    nx = dem_dr.width
    ny = dem_dr.height
    assert nx == gdir.grid.nx
    assert ny == gdir.grid.ny

    # Correct the DEM
    # Currently we just do a linear interp -- filling is totally shit anyway
    min_z = -999.
    dem[dem <= min_z] = np.NaN
    isfinite = np.isfinite(dem)
    if np.sum(~isfinite) > (percent_nans/100 * nx * ny):
        return 0
    else:
        return 1


def gdirs_from_tar_files(path):

    gdirs = []
    for regdir in os.listdir(path):

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
    df = pd.DataFrame([], columns=utils.DEM_SOURCES)

    logfile = (os.path.join(gdir.dir, 'log.txt'))

    # read logfile
    lfdf = pd.read_csv(logfile, delimiter=';', header=None,
                       skipinitialspace=True)

    # loop over dems and save existing ones to test
    dem2test = []
    for _, line in lfdf.iterrows():
        if 'DEM SOURCE' in line[1]:
            rgi = line[1].split(',')[0]
            dem = line[1].split(',')[2]
            dem2test.append(dem)

    # loop over DEMs
    for dem in dem2test:
        demfile = os.path.join(gdir.dir, dem) + '/dem.tif'
        df.loc[rgi, dem] = dem_quality_check(gdir, demfile)

    return df

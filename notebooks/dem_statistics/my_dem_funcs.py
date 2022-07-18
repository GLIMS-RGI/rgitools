# This script has been created by Matthias Dusch(https://github.com/matthiasdusch)
import os
import tarfile
import logging

import numpy as np
import pandas as pd
import rasterio

from oggm import utils, GlacierDirectory, entity_task

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
def check_all_dems_per_gdir(gdir):
    """Will go through all available DEMs and create some metrics

    DEMs musst be in GDir subfolders

    :param gdir:
    :return:
    """
    # dataframe for results
    df = pd.DataFrame([], index=[gdir.rgi_id]*6, # np.arange(3),
                      columns=['metric'] + utils.DEM_SOURCES)
    df.iloc[0]['metric'] = 'quality'
    df.iloc[1]['metric'] = 'quality_glc'
    df.iloc[2]['metric'] = 'meanhgt'
    df.iloc[3]['metric'] = 'meanhgt_glc'
    df.iloc[4]['metric'] = 'roughness'
    df.iloc[5]['metric'] = 'roughness_glc'

    logfile = (os.path.join(gdir.dir, 'log.txt'))

    # read logfile, specify names cause log entries have different size
    lfdf = pd.read_csv(logfile, delimiter=';', header=None,
                       skipinitialspace=True, names=[0, 1, 2, 3])

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
        qual, qualglc, hgt, hgt_glc, rgh, rgh_glc = dem_quality(gdir, demfile)
        df.loc[df.metric == 'quality', dem] = qual
        df.loc[df.metric == 'quality_glc', dem] = qualglc
        df.loc[df.metric == 'meanhgt', dem] = hgt
        df.loc[df.metric == 'meanhgt_glc', dem] = hgt_glc
        df.loc[df.metric == 'roughness', dem] = rgh
        df.loc[df.metric == 'roughness_glc', dem] = rgh_glc

    return df


def dem_barplot(df, ax, title=''):

    # dfexist = (df > 0).sum().sort_index()
    dfgood = (df > 0.9).sum().sort_index()

    # ax.bar(dfexist.index, dfexist.values, width=-0.4, align='edge',
    #        label='DEM exists')
    # ax.bar(dfgood.index, dfgood.values, width=0.4, align='edge', color='C2',
    #        label='DEM with >= 90% valid pixels')
    ax.bar(dfgood.index, dfgood.values, width=0.8, align='center', color='C0',
           label='DEM with >= 90% valid pixels')

    ax.set_ylabel('# number of glaciers')
    # ax.set_ylim([0, np.ceil(len(df)/50)*50])
    ax.set_ylim([0, len(df)])
    ax.set_xticklabels(dfgood.index, rotation=75)
    ax.set_title(title)
    # ax.legend(loc=3)

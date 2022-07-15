# This script has originally been created by Matthias Dusch(https://github.com/matthiasdusch) and got modified
# for the creation of dems_v2 statistics
import os
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt

from oggm.cli.prepro_levels import run_prepro_levels
from oggm import utils, cfg, GlacierDirectory
from oggm.workflow import execute_entity_task

from my_dem_funcs import (check_all_dems_per_gdir, gdirs_from_tar_files,
                          get_dem_area)
import statistics_paths


def parse_logfile(path, df=None):

    # df passed or new one?
    if df is None:
        df = pd.DataFrame([], columns=utils.DEM_SOURCES)

    for lf in os.listdir(path):
        # get rgi id from file name
        if '.ERROR' in lf:
            rgi = lf.split('.ERROR')[0]
        else:
            raise RuntimeError

        # read logfile
        lfdf = pd.read_csv(os.path.join(path, lf), delimiter=';', header=None,
                           skipinitialspace=True)

        # set all DEMs to True
        df.loc[rgi, :] = True

        # loop over dems and set erroneous ones to False
        for _, dem in lfdf.iterrows():
            print(dem[3])
            if dem[2] == 'InvalidDEMError':
                df.loc[rgi, dem[3].split()[1]] = False
            if 'HTTPSConnect' in dem[3]:
                print(rgi)

    return df


def parse_logfiles(path):

    df = pd.DataFrame([], columns=utils.DEM_SOURCES)

    for root, dirs, files in os.walk(path):
        if 'log.txt' in files:
            logfile = (os.path.join(root, 'log.txt'))

            # read logfile
            lfdf = pd.read_csv(logfile, delimiter=';', header=None,
                               skipinitialspace=True)

            # loop over dems and set erroneous ones to False
            for _, line in lfdf.iterrows():
                if 'DEM SOURCE' in line[1]:
                    rgi = line[1].split(',')[0]
                    dem = line[1].split(',')[2]
                    df.loc[rgi, dem] = True
                #elif 'InvalidDEMError' in line[2]:
                #    rgi = line[2].split()[-1]
                #    assert rgi[:3] == 'RGI'
                #    dem = line[2].split()[2]
                #    assert dem in df.columns
                #    df.loc[rgi, dem] = 0

    return df


def hgt_barplot(df1, df2, title='', savepath=None):

    fig, ax = plt.subplots(figsize=[10, 7])

    ax.bar(df1.index, df1.values, width=-0.4, align='edge',
           label='glaciated area (all DEMs >0.9 quality)', color='C0')
    ax.bar(df2.index, df2.values, width=0.4, align='edge', color='C1',
           label='full area (all DEMs >0.9 quality')

    ax.set_ylabel('elevation [m]')
    # ax.set_ylim([0, np.ceil(len(df)/5)*5])

    ax.set_title(title)
    ax.legend(loc=3)

    fig.tight_layout()
    if savepath is not None:
        fig.savefig(savepath)


wd = statistics_paths.wd
post = statistics_paths.post
sfx = statistics_paths.sfx
prepro_path = statistics_paths.prepro_path

os.makedirs(post, exist_ok=True)

cfg.initialize()
cfg.PATHS['working_dir'] = wd


dfarea = pd.DataFrame([], index=np.arange(1, 20), columns=['demarea'])

for reg in np.arange(1, 20):
    regstr = '{:02.0f}'.format(reg)

    try:
        rgidf = gpd.read_file(utils.get_rgi_region_file(regstr, version='6'))
        gdirs = [GlacierDirectory(rgiid) for rgiid in rgidf.RGIId]
        print('from gdir')
    except:
        gdirs = gdirs_from_tar_files(prepro_path, rgi_region=regstr)
        print('from tar')

    dfreg = execute_entity_task(check_all_dems_per_gdir, gdirs)
    dfreg = pd.concat(dfreg)

    quality = dfreg.loc[dfreg['metric'] == 'quality',
                        dfreg.columns != 'metric']

    hgt = dfreg.loc[dfreg['metric'] == 'meanhgt',
                    dfreg.columns != 'metric']

    qualityglc = dfreg.loc[dfreg['metric'] == 'quality_glc',
                           dfreg.columns != 'metric']
    hgtglc = dfreg.loc[dfreg['metric'] == 'meanhgt_glc',
                       dfreg.columns != 'metric']

    rgh = dfreg.loc[dfreg['metric'] == 'roughness',
                    dfreg.columns != 'metric']
    rghglc = dfreg.loc[dfreg['metric'] == 'roughness_glc',
                       dfreg.columns != 'metric']

    hgt_good = (hgt[(quality > 0.9)].dropna(axis=1, how='all').
                dropna(axis=0, how='any'))

    hgtglc_good = (hgtglc[(qualityglc > 0.9)].dropna(axis=1, how='all').
                   dropna(axis=0, how='any'))

    hgt_barplot(hgt_good.mean(), hgtglc_good.mean(),
                title=('Mean height of RGI region {} (#{:.0f} full area, ' +
                       '#{:.0f} glaciated area)').format(regstr,
                                                         len(hgt_good),
                                                         len(hgtglc_good)),
                savepath=os.path.join(post, 'rgi_hgt_%s.png' % (regstr + sfx)))

    rgi_area = np.sum([gd.rgi_area_km2 for gd in gdirs])

    dem_area = np.sum(execute_entity_task(get_dem_area, gdirs))

    dfarea.loc[reg, 'demarea'] = dem_area

    quality.to_hdf(os.path.join(post, 'rgi_%s.h5' % (regstr + sfx)),
                   mode='a', key='quality')

    qualityglc.to_hdf(os.path.join(post, 'rgi_%s.h5' % (regstr + sfx)),
                      mode='a', key='quality_glc')

    hgt.to_hdf(os.path.join(post, 'rgi_%s.h5' % (regstr + sfx)),
               mode='a', key='mhgt')

    hgtglc.to_hdf(os.path.join(post, 'rgi_%s.h5' % (regstr + sfx)),
                  mode='a', key='mhgt_glc')

    rgh.to_hdf(os.path.join(post, 'rgi_%s.h5' % (regstr + sfx)),
               mode='a', key='roughness')

    rghglc.to_hdf(os.path.join(post, 'rgi_%s.h5' % (regstr + sfx)),
                  mode='a', key='roughness_glc')


dfarea.to_hdf(os.path.join(post, 'dem_area{}.h5'.format(sfx)), key='demarea')

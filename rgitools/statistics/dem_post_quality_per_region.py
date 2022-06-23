import os
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt

from oggm import utils, cfg

from my_dem_funcs import dem_barplot


wd = '/home/alex/atmo_master/rgi_job/wd'
post_folder = '/home/alex/atmo_master/rgi_job/rgitools/rgitools/statistics/post'
cfg.initialize()
cfg.PATHS['working_dir'] = wd
# gdirs storage path(the 'path' variable shouldn't have to be used in this script)
# path = '/home/users/afischer/runs/rgitopo_creation_2/rgitopo_v2/RGI62/b_010/L1'
sfx = '_v1_highres'

# dataframe for all areas
dfall = pd.DataFrame()

# dataframe for statistic
cols = utils.DEM_SOURCES.copy()
cols.sort()
cols = ['RGI region', '# total'] + cols
dfstat = pd.DataFrame([], columns=cols)

# statistic on subregions
dfsub = dfstat.copy()

# rgi region file
regions = gpd.read_file('/media/alex/alexsd400/rgi/00_rgi62_regions/00_rgi62_O1Regions.shp')
subregs = gpd.read_file('/media/alex/alexsd400/rgi/00_rgi62_regions/00_rgi62_O2Regions.shp')

fig0, ax0 = plt.subplots(1, 1, figsize=[10, 10])

for reg in np.arange(1, 20):
    fig, ax = plt.subplots(1, 1, figsize=[10, 10])
    regstr = '{:02.0f}'.format(reg)

    quality = pd.read_hdf(os.path.join(post_folder, 'rgi_{}.h5'.format(regstr + sfx)),
                          'quality')
    regname = regions.loc[regions['RGI_CODE'].astype('int') == reg, 'FULL_NAME'].iloc[0]

    dem_barplot(quality, ax,
                title='RGI region {}: {} ({:.0f} glaciers)'.
                format(regstr, regname, len(quality)))
    fig.tight_layout()
    fig.savefig('/home/alex/atmo_master/rgi_job/rgitools/rgitools/statistics/post/out/images/' +
                'barplot_rgi{}.png'.format(regstr + sfx))

    dfall = dfall.append(quality)

    # FULL REGION
    total = len(quality)
    good = (quality > 0.9).sum()

    # out = good / total
    out = (good / total * 100).dropna().astype(int)
    outstr = out.astype(str)
    outstr.loc[out != 0] += '%'
    outstr.loc[out == 0] = '--'
    outstr['# total'] = total

    dfstat.loc[':ref:`{0}: {1}<rgi{0}>`'.format(regstr, regname)] = outstr

    # take care of subregions
    regdf = gpd.read_file(utils.get_rgi_region_file(regstr))
    sregs = np.unique(regdf.O2Region)

    for sreg in sregs:
        from IPython import embed; embed()
        ids = regdf.loc[regdf.O2Region == sreg, 'RGIId'].values
        subq = quality.loc[ids]

        # SUBREGIONS
        total = len(subq)
        good = (subq > 0.9).sum()
        out = (good / total * 100).dropna().astype(int)
        outstr = out.astype(str)
        outstr.loc[out != 0] += '%'
        outstr.loc[out == 0] = '--'
        outstr['# total'] = total

        subregstr = '-{:02.0f}'.format(int(sreg))
        subregname = subregs.loc[subregs.RGI_CODE == regstr + subregstr].\
            FULL_NAME.iloc[0]

        dfsub.loc['{}: {}'.format(regstr + subregstr, subregname)] = outstr

# FULL RGI
total = len(dfall)
good = (dfall > 0.9).sum()
out = (good / total * 100).dropna().astype(int)
outstr = out.astype(str)
outstr.loc[out != 0] += '%'
outstr.loc[out == 0] = '--'
outstr['# total'] = total

dfstat.loc['All RGI regions'] = outstr

dfsub.sort_index(inplace=True)

# integer for number of glaciers
dfstat['# total'] = dfstat['# total'].astype(int)
dfstat['RGI region'] = dfstat.index
dfsub['# total'] = dfsub['# total'].astype(int)
dfsub['RGI region'] = dfsub.index


# write csv files for RST readthedocs
dfstat.to_csv('/home/alex/atmo_master/rgi_job/rgitools/rgitools/statistics/post/out/tables/dem_allrgi{}.csv'.format(sfx),
              index=False)

# write subregion tables:
for reg in np.arange(1, 20):
    regstr = '{:02.0f}'.format(reg)
    dfsub
    sub = dfsub.loc[dfsub.index.str.contains('{}-'.format(regstr))]
    sub.to_csv('/home/alex/atmo_master/rgi_job/rgitools/rgitools/statistics/post/out/tables/dem_rgi{}.csv'.format(regstr + sfx),
               index=False)

# make and save plots
dem_barplot(dfall, ax0,
            title='All RGI regions ({:.0f} glaciers)'.format(len(dfall)))

fig0.tight_layout()
fig0.savefig('/home/alex/atmo_master/rgi_job/rgitools/rgitools/statistics/post/out/images/' +
             'barplot_allregions{}.png'.format(sfx))

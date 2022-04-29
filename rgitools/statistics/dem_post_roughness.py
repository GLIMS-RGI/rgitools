import os
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt

from oggm import utils, cfg

from my_dem_funcs import dem_barplot


wd = '/home/matthias/rgi/wd'
cfg.initialize()
cfg.PATHS['working_dir'] = wd

# gdirs storage path
path = '/home/matthias/rgi/dems_v1/default/RGI62/b_010/L1'
brauch ich das?
sfx = '_v1'

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
regions = gpd.read_file(os.path.join(cfg.PATHS['rgi_dir'], 'RGIV60',
                                     '00_rgi60_regions',
                                     '00_rgi60_O1Regions.shp'))
subregs = gpd.read_file(os.path.join(cfg.PATHS['rgi_dir'], 'RGIV60',
                                     '00_rgi60_regions',
                                     '00_rgi60_O2Regions.shp'))

fig, axs = plt.subplots(5, 4, figsize=[20, 22])

for reg in np.arange(1, 20):
    regstr = '{:02.0f}'.format(reg)

    quality = pd.read_hdf(os.path.join(wd, 'rgi_{}.h5'.format(regstr)),
                          'quality')

    regname = regions.loc[regions['RGI_CODE'] == reg, 'FULL_NAME'].iloc[0]

    dem_barplot(quality, fig.get_axes()[reg],
                title='RGI region {}: {} ({:.0f} glaciers)'.
                format(regstr, regname, len(quality)))

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

    dfstat.loc['{}: {}'.format(regstr, regname)] = outstr

    # take care of subregions
    regdf = gpd.read_file(utils.get_rgi_region_file(regstr))
    sregs = np.unique(regdf.O2Region)

    for sreg in sregs:
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

# save one with and one without specific DEMs
spc = ['REMA', 'RAMP', 'ARCTICDEM', 'GIMP']

# general table
tbl1 = dfstat.loc[:, ~dfstat.columns.isin(spc)].to_latex(
    na_rep='--', index=False, longtable=True,
    column_format='l' + 7*'r')
# add title
ti1 = ('\n\\caption{Summary of all RGI regions. First column shows total '
       'number of '
       'glaciers per RGI region. The consecutive columns specify the '
       'availability of particular DEMs for a RGI region in percent of the '
       'total glaciers per region. Values are not rounded but truncated so '
       '99\\% ' 
       'could be just one missing glacier. Only DEMs with less than 10\\% '
       'missing values are considered.}\\\\\n'
       '\\label{tbl_general}\\\\\n')
tbl1 = tbl1.replace('\n', ti1, 1)
with open('/home/matthias/rgi/report/dem_rgi_general.tex', 'w') as tf:
    tf.write(tbl1)

# specific table
tbl2 = dfstat.iloc[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 18]].\
    loc[:, dfstat.columns.isin(['RGI region', '# total'] + spc)].to_latex(
    na_rep='--', index=False, longtable=True,
    column_format='l' + 5*'r')
# add title
ti2 = ('\n\\caption{Same as Table \\ref{tbl_general} but for specific '
       'regional DEMs only.}\\\\\n'
       '\\label{tbl_specific}\\\\\n')
tbl2 = tbl2.replace('\n', ti2, 1)

with open('/home/matthias/rgi/report/dem_rgi_spec.tex', 'w') as tf:
    tf.write(tbl2)

#
# subregions
# general table
tbl3 = dfsub.loc[:, ~dfsub.columns.isin(spc)].to_latex(
    na_rep='--', index=False, longtable=True,
    column_format='l' + 7*'r')
# add title
ti3 = ('\n\\caption{Same as Table \\ref{tbl_general} but splitted into RGI '
       'subregions.}\\\\\n'
       '\\label{tbl_general_sub}\\\\\n')
tbl3 = tbl3.replace('\n', ti3, 1)
with open('/home/matthias/rgi/report/dem_subrgi_general.tex', 'w') as tf:
    tf.write(tbl3)

# specific table
tbl4 = dfsub.iloc[np.append(np.arange(0, 43), np.arange(69, 87))].\
    loc[:, dfsub.columns.isin(['RGI region', '# total'] + spc)].to_latex(
    na_rep='--', index=False, longtable=True,
    column_format='l' + 5*'r')
# add title
ti4 = ('\n\\caption{Same as Table \\ref{tbl_specific} but splitted into '
       'RGI subregions.}\\\\\n'
       '\\label{tbl_specific_sub}\\\\\n')
tbl4 = tbl4.replace('\n', ti4, 1)

with open('/home/matthias/rgi/report/dem_subrgi_spec.tex', 'w') as tf:
    tf.write(tbl4)

# write csv files for RST readthedocs
dfstat.to_csv('/home/matthias/rgi/rgitools/docs/_static/tables/dem_rgi.csv',
              index=False)
dfsub.to_csv('/home/matthias/rgi/rgitools/docs/_static/tables/dem_subrgi.csv',
             index=False)

# make and save plots
dem_barplot(dfall, axs[0, 0],
            title='All RGI regions ({:.0f} glaciers)'.format(len(dfall)))

fig.tight_layout()
fig.savefig('/home/matthias/rgi/rgitools/docs/_static/images/' +
            'dem_all_regions.png')
fig.savefig('/home/matthias/rgi/report/dem_all_regions.pdf')

"""All rgitools tests.

We use the pytest package to run them.
"""
import os
import shutil
from distutils.version import LooseVersion

import pytest
import pandas as pd
import geopandas as gpd
import numpy as np
from numpy.testing import assert_equal, assert_allclose

import rgitools
from rgitools import funcs
from rgitools.funcs import get_demo_file, mkdir


def get_iceland_df(reduced=False):

    df = gpd.read_file(get_demo_file('RGI6_icecap.shp'))
    if reduced:
        df = df.loc[(df.CenLon < -19.45) & (df.CenLat < 63.7)]
    return df


def test_install():
    assert LooseVersion(rgitools.__version__) >= LooseVersion('0.0.0')
    assert rgitools.__isreleased__ in [False, True]


def test_correct_geometries(tmpdir):

    # Simple ice cap
    test_of = os.path.join(str(tmpdir), 'interfile.shp')
    df = get_iceland_df(reduced=True)
    out = funcs.check_geometries(df.copy(), to_file=test_of, job_id='test')
    assert len(out) == len(df)
    assert os.path.exists(test_of)
    assert np.all(out.check_geom == '')

    # All
    test_of = os.path.join(str(tmpdir), 'interfile2.shp')
    df = get_iceland_df()
    out = funcs.check_geometries(df.copy(), to_file=test_of, job_id='test')
    assert len(out) == len(df)
    assert os.path.exists(test_of)
    assert np.all(g.is_valid for g in out.geometry)


def test_correct_geometries_cli_args(tmpdir):

    from rgitools.cli import correct_geometries

    kwargs = correct_geometries.parse_args(['--input-dir', 'dd1',
                                            '--output-dir', 'dd2',
                                            ])

    assert kwargs['input_dir'] == 'dd1'
    assert kwargs['output_dir'] == 'dd2'
    assert kwargs['replace_str'] is None
    assert kwargs['n_processes'] is None

    kwargs = correct_geometries.parse_args(['--input-dir', 'dd1',
                                            '--output-dir', 'dd2',
                                            '--replace-str', 'r1', 'r2',
                                            '--n-processes', '8',
                                            ])

    assert kwargs['input_dir'] == 'dd1'
    assert kwargs['output_dir'] == 'dd2'
    assert kwargs['n_processes'] == 8
    assert kwargs['replace_str']('1r1') == '1r2'

    with pytest.raises(ValueError):
        correct_geometries.parse_args([])

    with pytest.raises(ValueError):
        correct_geometries.parse_args(['--input-dir', 'dd1'])

    with pytest.raises(ValueError):
        correct_geometries.parse_args(['--input-dir', 'dd1',
                                       '--output-dir', 'dd2',
                                       '--replace-str', 'r1',
                                       ]
                                      )


def test_correct_geometries_cli(tmpdir):

    from rgitools.cli import correct_geometries

    rgi_dir = os.path.join(str(tmpdir), 'RGIV60')
    rgi_reg_dir = os.path.join(str(tmpdir), 'RGIV60', '06_rgi60_Iceland')
    mkdir(rgi_reg_dir)
    for e in ['.shp', '.prj', '.dbf', '.shx']:
        shutil.copyfile(get_demo_file('RGI6_icecap' + e),
                        os.path.join(rgi_reg_dir, '06_rgi60_Iceland' + e))
    out_dir = os.path.join(str(tmpdir), 'RGIV61')

    def replace(s):
        return s.replace('rgi60', 'rgi61')

    correct_geometries.run(rgi_dir, out_dir, replace_str=replace)
    outf = os.path.join(out_dir, '06_rgi61_Iceland', '06_rgi61_Iceland.shp')
    assert os.path.exists(outf)

    # All
    df = get_iceland_df()
    out = gpd.read_file(outf)
    assert len(out) == len(df)
    assert np.all(g.is_valid for g in out.geometry)
    assert np.any(out.check_geom != '')


def test_intersects(tmpdir):

    # Simple ice cap
    df = get_iceland_df(reduced=True)
    test_of = os.path.join(str(tmpdir), 'interfile.shp')
    out = funcs.compute_intersects(df, to_file=test_of, job_id='test')

    assert len(out) >= len(df)
    assert os.path.exists(test_of)

    # All elements should have an intersect with something
    all_ids = np.append(out.RGIId_1.values, out.RGIId_2.values)
    all_ids = np.sort(np.unique(all_ids))
    assert_equal(np.sort(np.unique(df.RGIId.values)), all_ids)


def test_intersects_cli_args(tmpdir):

    from rgitools.cli import compute_intersects

    kwargs = compute_intersects.parse_args(['--input-dir', 'dd1',
                                            '--output-dir', 'dd2',
                                            ])

    assert kwargs['input_dir'] == 'dd1'
    assert kwargs['output_dir'] == 'dd2'
    assert kwargs['n_processes'] is None

    kwargs = compute_intersects.parse_args(['--input-dir', 'dd1',
                                            '--output-dir', 'dd2',
                                            '--n-processes', '8',
                                            ])

    assert kwargs['input_dir'] == 'dd1'
    assert kwargs['output_dir'] == 'dd2'
    assert kwargs['n_processes'] == 8

    with pytest.raises(ValueError):
        compute_intersects.parse_args([])

    with pytest.raises(ValueError):
        compute_intersects.parse_args(['--input-dir', 'dd1'])


def test_intersects_cli(tmpdir):

    from rgitools.cli import compute_intersects

    rgi_dir = os.path.join(str(tmpdir), 'RGIV60')
    rgi_reg_dir = os.path.join(str(tmpdir), 'RGIV60', '06_rgi60_Iceland')
    mkdir(rgi_reg_dir)
    for e in ['.shp', '.prj', '.dbf', '.shx']:
        shutil.copyfile(get_demo_file('RGI6_icecap' + e),
                        os.path.join(rgi_reg_dir, '06_rgi60_Iceland' + e))
    out_dir = os.path.join(str(tmpdir), 'RGIV60_intersects')
    compute_intersects.run(rgi_dir, out_dir)
    assert os.path.exists(os.path.join(out_dir, '06_rgi60_Iceland',
                                       'intersects_06_rgi60_Iceland.shp'))


def test_find_clusters():

    # Simple ice cap
    df = get_iceland_df(reduced=True)
    idf = funcs.compute_intersects(df)

    # Add dummy entries for testing
    idf = idf.append({'RGIId_1': 'd1', 'RGIId_2': 'd2'}, ignore_index=True)
    idf = idf.append({'RGIId_1': 'd1', 'RGIId_2': 'd3'}, ignore_index=True)
    out = funcs.find_clusters(idf)
    assert len(out) == 2
    assert len(out['d1']) == 3


def test_merge_clusters():

    # Simple ice cap
    df = get_iceland_df(reduced=True)

    # Save the area for testing later
    area_ref = df.Area.sum()

    # Add dummy entries for testing
    from shapely.affinity import translate
    idf = df.iloc[0].copy()
    idf['geometry'] = translate(idf.geometry, xoff=0.15, yoff=0.0)
    idf['RGIId'] = 'd1'
    df = df.append(idf, ignore_index=True)

    idf = df.iloc[1].copy()
    idf['geometry'] = translate(idf.geometry, xoff=0.15, yoff=0.01)
    idf['RGIId'] = 'd2'
    df = df.append(idf, ignore_index=True)

    # Intersects and go
    idf = funcs.compute_intersects(df)
    out = funcs.merge_clusters(df, idf)

    assert len(out) == 3
    assert_allclose(out.iloc[0].Area, area_ref)

    s1 = df.iloc[-2]
    s2 = out.loc[out.RGIId == 'd1'].iloc[0]
    assert_equal(s1.CenLat, s2.CenLat)
    assert_equal(s1.CenLon, s2.CenLon)
    assert s1.geometry.equals(s2.geometry)


def test_merge_clusters_all():

    # All
    df = get_iceland_df()

    # Intersects and go
    idf = funcs.compute_intersects(df)
    out = funcs.merge_clusters(df, idf)

    assert np.all(g.is_valid for g in out.geometry)
    assert np.all(g.type == 'Polygon' for g in out.geometry)


def test_zip_cli_args(tmpdir):

    from rgitools.cli import zip_rgi_dir

    kwargs = zip_rgi_dir.parse_args(['--input-dir', 'dd1',
                                     '--output-file', 'dd2',
                                     ])

    assert kwargs['input_dir'] == 'dd1'
    assert kwargs['output_file'] == 'dd2'

    with pytest.raises(ValueError):
        zip_rgi_dir.parse_args([])

    with pytest.raises(ValueError):
        zip_rgi_dir.parse_args(['--input-dir', 'dd1'])


def test_zip_cli(tmpdir):

    from rgitools.cli import zip_rgi_dir

    rgi_dir = os.path.join(str(tmpdir), 'rgi_61')
    outf = os.path.join(str(tmpdir), 'rgi_61')

    regdirs = ['06_rgi61_Iceland', '07_rgi61_Scandinavia']
    for regdir in regdirs:
        rgi_reg_dir = os.path.join(rgi_dir, regdir)
        mkdir(rgi_reg_dir)
        for e in ['.shp', '.prj', '.dbf', '.shx']:
            shutil.copyfile(get_demo_file('RGI6_icecap' + e),
                            os.path.join(rgi_reg_dir, '01_rgi61_Iceland' + e))

    zip_rgi_dir.run(rgi_dir, outf)

    assert os.path.exists(outf)


def test_hypsometry(tmpdir):

    from oggm.utils import rmsd

    rgi_df = gpd.read_file(get_demo_file('rgi_oetztal.shp'))
    rgi_df = rgi_df.loc[['_d' not in rid for rid in rgi_df.RGIId]]

    outf = os.path.join(str(tmpdir), 'rgi_62')

    # Make if fail somewhere
    from shapely.affinity import translate
    geo = rgi_df.iloc[0, -1]
    rgi_df.iloc[0, -1] = translate(geo, xoff=10)
    rgi_df.loc[1, 'RGIFlag'] = '2909'

    def set_oggm_params(cfg):
        cfg.PATHS['dem_file'] = get_demo_file('srtm_oetztal.tif')
        cfg.PARAMS['use_multiprocessing'] = False

    df, gdf = funcs.hypsometries(rgi_df, set_oggm_params=set_oggm_params,
                                 to_file=outf)

    assert np.all(df.loc[0, df.columns[3:]] == -9)
    assert np.all(df.loc[1, df.columns[3:]] == -9)
    assert not np.isfinite(gdf.loc[0, 'Aspect'])
    assert gdf.loc[1, 'Aspect'] == rgi_df.loc[1, 'Aspect']
    df = df.iloc[2:]
    assert np.all(df[df.columns[3:]].sum(axis=1) == 1000)

    gdf = gdf.iloc[2:]
    rgi_df = rgi_df.iloc[2:]

    assert rmsd(gdf['Zmed'], rgi_df['Zmed']) < 25
    assert rmsd(gdf['Zmin'], rgi_df['Zmin']) < 25
    assert rmsd(gdf['Zmax'], rgi_df['Zmax']) < 25
    assert rmsd(gdf['Slope'], rgi_df['Slope']) < 1

    # For aspect test for cos / sin  because of 0 360 thing
    us = np.cos(np.deg2rad(gdf.Aspect))
    ref = np.cos(np.deg2rad(rgi_df.Aspect))
    assert rmsd(us, ref) < 0.3
    us = np.sin(np.deg2rad(gdf.Aspect))
    ref = np.sin(np.deg2rad(rgi_df.Aspect))
    assert rmsd(us, ref) < 0.3

    ##
    df = pd.read_csv(outf + '_hypso.csv')
    gdf = gpd.read_file(outf + '.shp')

    assert np.all(df.loc[0, df.columns[3:]] == -9)
    assert np.all(df.loc[1, df.columns[3:]] == -9)
    assert not np.isfinite(gdf.loc[0, 'Aspect'])
    df = df.iloc[2:]
    assert np.all(df[df.columns[3:]].sum(axis=1) == 1000)

    gdf = gdf.iloc[2:]

    assert rmsd(gdf['Zmed'], rgi_df['Zmed']) < 25
    assert rmsd(gdf['Zmin'], rgi_df['Zmin']) < 25
    assert rmsd(gdf['Zmax'], rgi_df['Zmax']) < 25
    assert rmsd(gdf['Slope'], rgi_df['Slope']) < 1

    # For aspect test for cos / sin  because of 0 360 thing
    us = np.cos(np.deg2rad(gdf.Aspect))
    ref = np.cos(np.deg2rad(rgi_df.Aspect))
    assert rmsd(us, ref) < 0.3
    us = np.sin(np.deg2rad(gdf.Aspect))
    ref = np.sin(np.deg2rad(rgi_df.Aspect))
    assert rmsd(us, ref) < 0.3


def set_oggm_params(cfg):
    cfg.PATHS['dem_file'] = get_demo_file('srtm_oetztal.tif')


def test_correct_hypsometries_cli_args(tmpdir):

    from rgitools.cli import compute_hypsometries

    kwargs = compute_hypsometries.parse_args(['--input-dir', 'dd1',
                                              '--output-dir', 'dd2',
                                              ])

    assert kwargs['input_dir'] == 'dd1'
    assert kwargs['output_dir'] == 'dd2'
    assert kwargs['replace_str'] is None
    assert kwargs['n_processes'] is None

    kwargs = compute_hypsometries.parse_args(['--input-dir', 'dd1',
                                              '--output-dir', 'dd2',
                                              '--replace-str', 'r1', 'r2',
                                              '--n-processes', '8',
                                              ])

    assert kwargs['input_dir'] == 'dd1'
    assert kwargs['output_dir'] == 'dd2'
    assert kwargs['n_processes'] == 8
    assert kwargs['replace_str']('1r1') == '1r2'

    with pytest.raises(ValueError):
        compute_hypsometries.parse_args([])

    with pytest.raises(ValueError):
        compute_hypsometries.parse_args(['--input-dir', 'dd1'])

    with pytest.raises(ValueError):
        compute_hypsometries.parse_args(['--input-dir', 'dd1',
                                         '--output-dir', 'dd2',
                                         '--replace-str', 'r1',
                                         ]
                                        )


def test_hypsometries_cli(tmpdir):

    from rgitools.cli import compute_hypsometries, correct_geometries

    rgi_dir = os.path.join(str(tmpdir), 'RGIV60')
    rgi_reg_dir = os.path.join(str(tmpdir), 'RGIV60', '11_rgi60_Europe')
    mkdir(rgi_reg_dir)
    for e in ['.shp', '.prj', '.dbf', '.shx']:
        shutil.copyfile(get_demo_file('rgi_oetztal' + e),
                        os.path.join(rgi_reg_dir, '11_rgi60_Europe' + e))
    tmp_dir = os.path.join(str(tmpdir), 'RGIV61')

    def replace(s):
        return s.replace('rgi60', 'rgi61')

    correct_geometries.run(rgi_dir, tmp_dir, replace_str=replace)
    outf = os.path.join(tmp_dir, '11_rgi61_Europe', '11_rgi61_Europe.shp')
    assert os.path.exists(outf)

    # All
    df = gpd.read_file(get_demo_file('rgi_oetztal.shp'))
    out = gpd.read_file(outf)
    assert len(out) == len(df)
    assert np.all(g.is_valid for g in out.geometry)
    assert np.any(out.check_geom != '')

    out_dir = os.path.join(str(tmpdir), 'RGIV62')

    def replace(s):
        return s.replace('rgi61', 'rgi62')

    compute_hypsometries.run(tmp_dir, out_dir,
                             replace_str=replace,
                             set_oggm_params=set_oggm_params)
    outf = os.path.join(out_dir, '11_rgi62_Europe', '11_rgi62_Europe.shp')
    assert os.path.exists(outf)
    outf = os.path.join(out_dir, '11_rgi62_Europe',
                        '11_rgi62_Europe_hypso.csv')
    assert os.path.exists(outf)
    outf = os.path.join(out_dir, '11_rgi62_Europe',
                        '11_rgi62_Europe_hypso.csv')
    assert os.path.exists(outf)

"""All rgitools tests.

We use the pytest package to run them.
"""
import os
import shutil
from distutils.version import LooseVersion

import geopandas as gpd
import numpy as np
from numpy.testing import assert_equal, assert_allclose

import rgitools
from rgitools import funcs, scripts
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


def test_correct_geometries_script(tmpdir):

    rgi_dir = os.path.join(str(tmpdir), 'RGIV60')
    rgi_reg_dir = os.path.join(str(tmpdir), 'RGIV60', '06_rgi60_Iceland')
    mkdir(rgi_reg_dir)
    for e in ['.shp', '.prj', '.dbf', '.shx']:
        shutil.copyfile(get_demo_file('RGI6_icecap' + e),
                        os.path.join(rgi_reg_dir, '06_rgi60_Iceland' + e))
    out_dir = os.path.join(str(tmpdir), 'RGIV61')

    def replace(s):
        return s.replace('rgi60', 'rgi61')

    scripts.correct_all_geometries(rgi_dir, out_dir, replace_str=replace)
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


def test_intersects_script(tmpdir):

    rgi_dir = os.path.join(str(tmpdir), 'RGIV60')
    rgi_reg_dir = os.path.join(str(tmpdir), 'RGIV60', '06_rgi60_Iceland')
    mkdir(rgi_reg_dir)
    for e in ['.shp', '.prj', '.dbf', '.shx']:
        shutil.copyfile(get_demo_file('RGI6_icecap' + e),
                        os.path.join(rgi_reg_dir, '06_rgi60_Iceland' + e))
    out_dir = os.path.join(str(tmpdir), 'RGIV60_intersects')
    scripts.compute_all_intersects(rgi_dir, out_dir)
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

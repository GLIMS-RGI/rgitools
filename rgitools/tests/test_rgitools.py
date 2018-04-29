"""All rgitools tests.

We use the pytest package to run them.
"""
import os
import shutil
from distutils.version import LooseVersion

import geopandas as gpd
import numpy as np
from numpy.testing import assert_equal
from oggm.utils import get_demo_file, mkdir

import rgitools
from rgitools import funcs, scripts


def test_install():
    assert LooseVersion(rgitools.__version__) >= LooseVersion('0.0.0')
    assert rgitools.__isreleased__ in [False, True]


def test_intersects(tmpdir):
    test_of = os.path.join(str(tmpdir), 'interfile.shp')
    df = gpd.read_file(get_demo_file('RGI6_icecap.shp'))
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
    scripts.write_intersects_to_dir(rgi_dir, out_dir)
    assert os.path.exists(os.path.join(out_dir, '06_rgi60_Iceland',
                                       'intersects_06_rgi60_Iceland.shp'))

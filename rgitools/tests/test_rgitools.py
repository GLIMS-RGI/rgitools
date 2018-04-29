"""All rgitools tests.

We use the pytest package to run them.
"""
from distutils.version import LooseVersion

import geopandas as gpd
import numpy as np
from numpy.testing import assert_equal
from oggm.utils import get_demo_file

import rgitools


def test_install():
    assert LooseVersion(rgitools.__version__) >= LooseVersion('0.0.0')
    assert rgitools.__isreleased__ in [False, True]


def test_intersects():
    df = gpd.read_file(get_demo_file('RGI6_icecap.shp'))
    out = rgitools.compute_intersects(df)

    # All elements should have an intersect with something
    assert len(out) >= len(df)
    all_ids = np.append(out.RGIId_1.values, out.RGIId_2.values)
    all_ids = np.sort(np.unique(all_ids))
    assert_equal(np.sort(np.unique(df.RGIId.values)), all_ids)

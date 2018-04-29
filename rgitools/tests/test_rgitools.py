"""All rgitools tests.

We use the pytest package to run them.
"""
from distutils.version import LooseVersion
import rgitools


def test_install():
    assert LooseVersion(rgitools.__version__) >= LooseVersion('0.0.0')

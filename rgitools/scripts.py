import os
from glob import glob
import multiprocessing as mp

from oggm.utils import mkdir

from rgitools import funcs


def correct_all_geometries(rgi_dir, out_dir, n_processes=None):
    """Corrects the geometries for an entire RGI directory.

    Parameters
    ----------
    rgi_dir : str
        path to the RGI directory
    out_dir : str
        path to the output directory
    n_processes : int, optional
        the number of processors to use
    """

    # Download RGI files
    fp = '*_rgi*_*.shp'
    rgi_shps = list(glob(os.path.join(rgi_dir, "*", fp)))
    rgi_shps = sorted([r for r in rgi_shps if 'Regions' not in r])

    mkdir(out_dir)

    out_paths = []
    log_names = []
    for rgi_shp in rgi_shps:
        odir = os.path.basename(os.path.dirname(rgi_shp))
        odir = os.path.join(out_dir, odir)
        mkdir(odir)
        bn = os.path.basename(rgi_shp)
        of = os.path.join(odir, bn)
        out_paths.append(of)
        log_names.append(bn)

    with mp.Pool(n_processes) as p:
        p.starmap(funcs.check_geometries,
                  zip(rgi_shps, out_paths, log_names),
                  chunksize=1)


def compute_all_intersects(rgi_dir, out_dir, n_processes=None):
    """Computes the intersects for an entire RGI directory.

    Parameters
    ----------
    rgi_dir : str
        path to the RGI directory
    out_dir : str
        path to the output directory
    n_processes : int, optional
        the number of processors to use
    """

    # Download RGI files
    fp = '*_rgi*_*.shp'
    rgi_shps = list(glob(os.path.join(rgi_dir, "*", fp)))
    rgi_shps = sorted([r for r in rgi_shps if 'Regions' not in r])

    mkdir(out_dir)

    out_paths = []
    log_names = []
    for rgi_shp in rgi_shps:
        odir = os.path.basename(os.path.dirname(rgi_shp))
        odir = os.path.join(out_dir, odir)
        mkdir(odir)
        bn = os.path.basename(rgi_shp)
        of = os.path.join(odir, 'intersects_' + bn)
        out_paths.append(of)
        log_names.append(bn)

    with mp.Pool(n_processes) as p:
        p.starmap(funcs.compute_intersects,
                  zip(rgi_shps, out_paths, log_names),
                  chunksize=1)

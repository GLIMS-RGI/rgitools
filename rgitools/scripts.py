import os
from glob import glob
import multiprocessing as mp

from oggm.utils import mkdir

from rgitools import funcs


def write_intersects_to_dir(rgi_dir, out_dir):

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

    with mp.Pool() as p:
        p.starmap(funcs.compute_intersects,
                  zip(rgi_shps, out_paths, log_names),
                  chunksize=1)

import os
import sys
from glob import glob
import argparse
import multiprocessing as mp

from rgitools import funcs


def run(input_dir=None, output_dir=None, *, n_processes=None):
    """Computes the intersects for an entire RGI directory.

    Parameters
    ----------
    input_dir : str
        path to the RGI directory
    output_dir : str
        path to the output directory
    n_processes : int, optional
        the number of processors to use
    """

    # Download RGI files
    fp = '*_rgi*_*.shp'
    rgi_shps = list(glob(os.path.join(input_dir, "*", fp)))
    rgi_shps = sorted([r for r in rgi_shps if 'Regions' not in r])

    funcs.mkdir(output_dir)

    out_paths = []
    log_names = []
    for rgi_shp in rgi_shps:
        odir = os.path.basename(os.path.dirname(rgi_shp))
        odir = os.path.join(output_dir, odir)
        funcs.mkdir(odir)
        bn = os.path.basename(rgi_shp)
        of = os.path.join(odir, 'intersects_' + bn)
        out_paths.append(of)
        log_names.append(bn)

    with mp.Pool(n_processes) as p:
        p.starmap(funcs.mappable_func,
                  zip([funcs.compute_intersects] * len(rgi_shps),
                      rgi_shps, out_paths, log_names),
                  chunksize=1)


def parse_args(args):
    """Check input arguments"""

    # CLI args
    description = 'Computes the intersects for an entire RGI directory.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--input-dir', type=str,
                        help='the rgi directory to process.')
    parser.add_argument('--output-dir', type=str,
                        help='the directory where to write the processed '
                             'files.')
    parser.add_argument('--n-processes', type=int,
                        help='Number of processors to use.')
    args = parser.parse_args(args)

    if not args.input_dir:
        raise ValueError('--input-dir is required!')

    if not args.output_dir:
        raise ValueError('--output-dir is required!')

    # All good
    return dict(input_dir=args.input_dir, output_dir=args.output_dir,
                n_processes=args.n_processes)


def main():
    """Script entry point"""

    run(**parse_args(sys.argv[1:]))

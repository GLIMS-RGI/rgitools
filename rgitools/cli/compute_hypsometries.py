import os
import sys
from glob import glob
import argparse
import multiprocessing as mp

from rgitools import funcs


def _set_oggm_params(cfg):
    cfg.PARAMS['use_multiprocessing'] = False


def run(input_dir=None, output_dir=None, *, replace_str=None,
        oggm_working_dir='', set_oggm_params=None,
        n_processes=None):
    """Computes the hypsometries for an entire RGI directory.

    Parameters
    ----------
    input_dir : str
        path to the RGI directory
    output_dir : str
        path to the output directory
    replace_str : callable
        a function to call on the file's basename. A good example is:
        ``replace_str=lambda x : x.replace('rgi60', 'rgi61')``
    oggm_working_dir : str
        str, optional
        path to the folder where oggm will write its GlacierDirectories.
        Default is to use a temporary folder (not recommended)
    set_oggm_params : callable
        a function which sets the OGGM params on cfg. The default is to
        turn multiprocessing off.
    n_processes : int, optional
        the number of processors to use
    """

    # Input check
    if set_oggm_params is None:
        set_oggm_params = _set_oggm_params

    # Get RGI files
    fp = '*_rgi*_*.shp'
    rgi_shps = list(glob(os.path.join(input_dir, "*", fp)))

    rgi_shps = sorted([r for r in rgi_shps if 'Regions' not in r])

    funcs.mkdir(output_dir)

    out_paths = []
    log_names = []
    for rgi_shp in rgi_shps:
        odir = os.path.basename(os.path.dirname(rgi_shp))
        if replace_str:
            odir = replace_str(odir)
        odir = os.path.join(output_dir, odir)
        funcs.mkdir(odir)
        bn = os.path.basename(rgi_shp)
        if replace_str:
            bn = replace_str(bn)
        bn = bn.replace('.shp', '')
        of = os.path.join(odir, bn)
        out_paths.append(of)
        log_names.append(bn)

    with mp.Pool(n_processes) as p:
        p.starmap(funcs.mappable_func,
                  zip([funcs.hypsometries] * len(rgi_shps),
                      rgi_shps, out_paths, log_names,
                      [set_oggm_params] * len(rgi_shps),
                      [oggm_working_dir] * len(rgi_shps),
                      ),
                  chunksize=1)


def parse_args(args):
    """Check input arguments"""

    # CLI args
    description = 'Computes the hypsometries for an entire RGI directory.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--input-dir', type=str,
                        help='the rgi directory to process.')
    parser.add_argument('--output-dir', type=str,
                        help='the directory where to write the processed '
                             'files.')
    parser.add_argument('--oggm-working-dir', type=str,
                        help='the directory where to write the processed '
                             'files.')
    parser.add_argument('--replace-str', nargs='*', type=str,
                        help='a string to change on the file basename. '
                             'A good example is: --replace-str rgi60 rgi61')
    parser.add_argument('--n-processes', type=int,
                        help='Number of processors to use.')
    args = parser.parse_args(args)

    if not args.input_dir:
        raise ValueError('--input-dir is required!')

    if not args.output_dir:
        raise ValueError('--output-dir is required!')

    if args.replace_str:
        if len(args.replace_str) != 2:
            raise ValueError('--replace-str needs two values!')
        s1, s2 = args.replace_str
        replace_str = lambda x: x.replace(s1, s2)
    else:
        replace_str = None

    # All good
    return dict(input_dir=args.input_dir, output_dir=args.output_dir,
                replace_str=replace_str, n_processes=args.n_processes,
                oggm_working_dir=args.oggm_working_dir)


def main():
    """Script entry point"""

    run(**parse_args(sys.argv[1:]))

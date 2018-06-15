import os
import shutil
import tempfile
from glob import glob
import multiprocessing as mp

from rgitools import funcs


def mappable_func(*args):
    """Wrapper to unpack kwargs and pass them to args[0]"""
    kwargs = dict(to_file=args[2], job_id=args[3])
    return args[0](args[1], **kwargs)


def correct_all_geometries(rgi_dir, out_dir, replace_str=None,
                           n_processes=None):
    """Corrects the geometries for an entire RGI directory.

    Parameters
    ----------
    rgi_dir : str
        path to the RGI directory
    out_dir : str
        path to the output directory
    replace_str : callable
        a function to call on the file's basename. A good example is:
        ``replace_str=lambda x : x.replace('rgi60', 'rgi61')``
    n_processes : int, optional
        the number of processors to use
    """

    # Download RGI files
    fp = '*_rgi*_*.shp'
    rgi_shps = list(glob(os.path.join(rgi_dir, "*", fp)))
    rgi_shps = sorted([r for r in rgi_shps if 'Regions' not in r])

    funcs.mkdir(out_dir)

    out_paths = []
    log_names = []
    for rgi_shp in rgi_shps:
        odir = os.path.basename(os.path.dirname(rgi_shp))
        if replace_str:
            odir = replace_str(odir)
        odir = os.path.join(out_dir, odir)
        funcs.mkdir(odir)
        bn = os.path.basename(rgi_shp)
        if replace_str:
            bn = replace_str(bn)
        of = os.path.join(odir, bn)
        out_paths.append(of)
        log_names.append(bn)

    with mp.Pool(n_processes) as p:
        p.starmap(mappable_func,
                  zip([funcs.check_geometries] * len(rgi_shps),
                      rgi_shps, out_paths, log_names),
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

    funcs.mkdir(out_dir)

    out_paths = []
    log_names = []
    for rgi_shp in rgi_shps:
        odir = os.path.basename(os.path.dirname(rgi_shp))
        odir = os.path.join(out_dir, odir)
        funcs.mkdir(odir)
        bn = os.path.basename(rgi_shp)
        of = os.path.join(odir, 'intersects_' + bn)
        out_paths.append(of)
        log_names.append(bn)

    with mp.Pool(n_processes) as p:
        p.starmap(mappable_func,
                  zip([funcs.compute_intersects] * len(rgi_shps),
                      rgi_shps, out_paths, log_names),
                  chunksize=1)


def compute_all_hypsometries(rgi_dir, out_dir, replace_str=None,
                             oggm_working_dir='', set_oggm_params=None,
                             n_processes=None):
    """Computes the hypsometries for an entire RGI directory.

    Parameters
    ----------
    rgi_dir : str
        path to the RGI directory
    out_dir : str
        path to the output directory
    replace_str : callable
        a function to call on the file's basename. A good example is:
        ``replace_str=lambda x : x.replace('rgi60', 'rgi61')``
    """

    # Get RGI files
    fp = '*_rgi*_*.shp'
    rgi_shps = list(glob(os.path.join(rgi_dir, "*", fp)))

    rgi_shps = sorted([r for r in rgi_shps if 'Regions' not in r])

    funcs.mkdir(out_dir)

    out_paths = []
    log_names = []
    for rgi_shp in rgi_shps:
        odir = os.path.basename(os.path.dirname(rgi_shp))
        if replace_str:
            odir = replace_str(odir)
        odir = os.path.join(out_dir, odir)
        funcs.mkdir(odir)
        bn = os.path.basename(rgi_shp)
        if replace_str:
            bn = replace_str(bn)
        bn = bn.replace('.shp', '')
        of = os.path.join(odir, bn)
        out_paths.append(of)
        log_names.append(bn)

    with mp.Pool(n_processes) as p:
        p.starmap(mappable_func,
                  zip([funcs.hypsometries] * len(rgi_shps),
                      rgi_shps, out_paths, log_names,
                      [set_oggm_params] * len(rgi_shps),
                      [oggm_working_dir] * len(rgi_shps),
                      ),
                  chunksize=1)


def zip_rgi_dir(rgi_dir, out_file, manifest=''):
    """Zips an RGI directory and makes it look like a real one.

    Parameters
    ----------
    rgi_dir : str
        path to the RGI directory
    out_file : str
        path to the output file (without zip ending!)
    manifest : str
        text to put in the manifest
    """

    # First zip the regions
    bname = os.path.basename(rgi_dir)
    tmpdir = tempfile.mkdtemp()
    workdir = os.path.join(tmpdir, bname)
    funcs.mkdir(tmpdir, reset=True)
    for reg_dir in os.listdir(rgi_dir):
        zipf = os.path.join(workdir, reg_dir)
        reg_dir = os.path.join(rgi_dir, reg_dir)
        shutil.make_archive(zipf, 'zip', reg_dir)

    # Make the manifest file
    mpath = os.path.join(workdir, '000_' + bname + '_manifest.txt')
    with open(mpath, 'w') as file:
        file.write(manifest)

    # Compress the working directory
    shutil.make_archive(out_file, 'zip', workdir)

    # Delete our working dir
    shutil.rmtree(tmpdir)

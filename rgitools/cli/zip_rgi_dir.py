import os
import sys
import shutil
import tempfile
import argparse

from rgitools import funcs


def run(input_dir, output_file):
    """Zips an RGI directory and makes it look like a real one.

    Parameters
    ----------
    input_dir : str
        path to the RGI directory
    output_file : str
        path to the output file (without zip ending!)
    """

    # First zip the directories and copy the files
    bname = os.path.basename(input_dir)
    tmpdir = tempfile.mkdtemp()
    workdir = os.path.join(tmpdir, bname)
    funcs.mkdir(workdir, reset=True)
    for fname in os.listdir(input_dir):
        abs_p = os.path.join(input_dir, fname)
        out_f = os.path.join(workdir, fname)
        if os.path.isfile(abs_p):
            shutil.copy(abs_p, out_f)
        else:
            shutil.make_archive(out_f, 'zip', abs_p)

    # Compress the working directory
    shutil.make_archive(output_file, 'zip', workdir)

    # Delete our working dir
    shutil.rmtree(tmpdir)


def parse_args(args):
    """Check input arguments"""

    # CLI args
    description = 'Computes the intersects for an entire RGI directory.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--input-dir', type=str,
                        help='the rgi directory to process.')
    parser.add_argument('--output-file', type=str,
                        help='path to the output file (without zip ending!)')
    args = parser.parse_args(args)

    if not args.input_dir:
        raise ValueError('--input-dir is required!')

    if not args.output_file:
        raise ValueError('--output-file is required!')

    # All good
    return dict(input_dir=args.input_dir, output_file=args.output_file)


def main():
    """Script entry point"""

    run(**parse_args(sys.argv[1:]))

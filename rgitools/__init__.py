try:
    from .version import version as __version__
    from .version import isreleased as __isreleased__
except ImportError:
    raise ImportError('rgitools is not properly installed. If you are running '
                      'from the source directory, please instead create a '
                      'new virtual environment (using conda or virtualenv) '
                      'and  then install it in-place by running: '
                      'pip install -e .')

API reference
=============

Package structure
-----------------

The package is structured in two modules:

- **rgitools.funcs**, which contains standalone functions acting on one single
  shapefile
- **rgitools.cli**, which contains scripts acting on an RGI directory and
  calling ``rgitools.funcs`` in a multi-processing loop. These scripts can
  be called from the command line: type `rgitools + TAB` for a listing


API reference
=============

Package structure
-----------------

The package is structured in two modules:

- **rgitools.funcs**, which contains standalone functions acting on one single
  shapefile, and
- **rgitools.scripts**, which contains scripts acting on an RGI directory and
  calling ``rgitools.funcs`` in a multi-processing loop.

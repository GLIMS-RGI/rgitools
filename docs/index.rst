
rgitools: processing files from the Randolph Glacier Inventory
--------------------------------------------------------------

`rgitools <https://github.com/OGGM/rgitools>`_ provides several tools to
(pre-)process and analyse the glacier outlines provided by the
`Randolph Glacier Inventory <https://www.glims.org/RGI/>`_ (RGI).

It is currently in development, but our goal is to provide the following
services to the RGI community:

- **automated data quality check**: see :ref:`tools.qc`.
- **Geometry of the ice divides and listing or glacier clusters**:
  see :ref:`tools.intersects`.
- **Merging of glacier clusters**: see :ref:`tools.merge`.
- **Glacier hypsometry from DEM**: see :ref:`tools.hypso`.
- **Gridded topography data for each glacier**: see :ref:`dems`.
- **ID link list between RGI versions** (not available yet)


Documentation
-------------

.. toctree::
    :maxdepth: 1

    installing
    tools
    known-issues
    dems
    api
    whats-new


Get in touch
------------

- View the source code `on GitHub`_.
- Report bugs or share your ideas on the `issue tracker`_.
- Improve the model by submitting a `pull request`_.
- Follow us on `Twitter`_.
- Or you can always send us an `e-mail`_ the good old way.

.. _e-mail: info@oggm.org
.. _on GitHub: https://github.com/OGGM/rgitools
.. _issue tracker: https://github.com/OGGM/rgitools/issues
.. _pull request: https://github.com/OGGM/rgitools/pulls
.. _Twitter: https://twitter.com/OGGM_org


About
-----

:Tests:
    .. image:: https://travis-ci.org/OGGM/rgitools.svg?branch=master
        :target: https://travis-ci.org/OGGM/rgitools
        :alt: Linux build status

:Documentation:
    .. image:: https://readthedocs.org/projects/rgitools/badge/?version=latest
        :target: http://rgitools.readthedocs.org/en/latest/?badge=latest
        :alt: Documentation status

:License:
    .. image:: https://img.shields.io/pypi/l/rgitools.svg
        :target: https://github.com/OGGM/rgitools/blob/master/LICENSE.txt
        :alt: BSD-3-Clause License

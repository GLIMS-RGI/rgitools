Installing rgitools
===================

rgitools relies on the same packages as OGGM. Refer to the
`installation page of OGGM <http://oggm.readthedocs.io/en/latest/installing-oggm.html>`_
first, then do::

    pip install git+https://github.com/OGGM/rgitools.git


Development version
~~~~~~~~~~~~~~~~~~~

**If you want to explore the code or participate to its
development**, we recommend to clone the git repository (or your own fork)::

    git clone https://github.com/OGGM/rgitools.git

Then go to the project root directory::

    cd rgitools

And install rgitools in development mode (this is valid for **pip** or
**conda** environments)::

    pip install -e .


You are almost there! The last step is to check if everything works as
expected. From the rgitools directory, type::

    pytest .

If everything worked fine, you should see something like::

    ============================= test session starts ==============================
    platform linux -- Python 3.5.2, pytest-3.5.0, py-1.5.3, pluggy-0.6.0
    Matplotlib: 2.2.2
    Freetype: 2.6.1
    rootdir: /home/mowglie/Documents/git/rgitools, inifile:
    plugins: mpl-0.9
    collected 9 items

    rgitools/tests/test_rgitools.py .........                                [100%]

    =========================== 9 passed in 6.57 seconds ===========================


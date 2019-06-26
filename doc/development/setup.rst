Developping in SBXG
===============================================================================

Setting-up the development environment
-------------------------------------------------------------------------------

SBXG is a python module, that requires python3.6 or higher. To make things
simple, we advise you develop in a `virtualenv
<https://virtualenv.pypa.io/en/stable/>`_.

You shall begin by installing python3.6 or higher on your platform. Recent
distributions should have it already installed. From now on, I assume that
the program ``python3`` is in your ``PATH``, and that running::

  python3 --version

yields something like::

  $ python3 --version
  Python 3.6.8

I will also assume that the associated program ``pip3`` (`pip
<https://pypi.org/project/pip/>`_ for python3) is installed and in your
``PATH``. Which means that running::

  pip3 --version

yields something like::

  $ pip3 --version
  pip 9.0.1 from /usr/lib/python3/dist-packages (python 3.6)

We now can install the virtualenv package, if it does not already exist::

  pip3 install --user virtualenv

Now, for every new clone of SBXG sources, you **must** create the virtualenv
in **the top source directory**::

  virtualenv --python=python3 .venv

This will have for effect to create the directory ``.venv/`` (which is already
described in the ``.gitignore`` file) and will contain your python environment
when developping in SBXG.

Then, **activate your virtualenv**. If you have a POSIX-compatible shell, run::

  . .venv/bin/activate

This will modify your current environment, so you can use the virtualenv.
From now on, the ``python`` and ``pip`` programs will be the ones of your
virtualenv! Not the ones of your system.

.. admonition:: Don't forget to activate your virtualenv!
  :class: warning

  For **every new interactive session** (i.e. when you open a new terminal to
  develop in SBXG), you **MUST** activate your virtualenv. Otherwise, you
  will not use it, and weird things may occur!

If you just created your virtualenv, you must install the appropriate python
dependencies::

  pip install -r utils/requirements.txt

And you are good to go!

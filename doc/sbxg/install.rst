How to install SBXG
===============================================================================

SBXG can be divided in two classes of components:

1. the core of SBXG itself, which is a python package; and
2. the run-time dependencies of SBXG, that are third-parties tools the generated
   build system will rely on.



Installing the dependencies
-------------------------------------------------------------------------------

Only GNU/Linux distributions are supported. You may want to use the command-line
that suits your distribution the best.

Debian-based distributions (including Ubuntu)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: sh

  sudo apt install git python3-pip make curl build-essential autoconf \
    autotools-dev tar swig python-dev libconfuse-dev mtools


Installing the SBXG python package
-------------------------------------------------------------------------------

.. admonition:: There are no pip package
   :class: warning

   Currently, there is no pip package on Pypi. You are obliged to build from
   sources!

Currently, the only way to install SBXG is by downloading the sources and
installing from these sources. So, you must have ``git`` and ``pip3`` installed.
Then, run the following commands::

  git clone https://github.com/sbxg/sbxg.git
  pip3 install --user -r sbxg/requirements.txt
  pip3 install --user sbxg


Understand the use of each dependency
-------------------------------------------------------------------------------

You may have noticed that SBXG requires quite some dependencies. We will
explain here in which context they are important.

**Python 3.6**
  SBXG is written in python. This is a no-brainer, without python 3.6 or higher,
  you will not be able to run SBXG at all.

**Make**
  SBXG bootstraps its build system, by generating a Makefile. Therefore,
  ``make`` (only GNU make is tested) is a strong requirement for SBXG. No
  ``make``, no possibiltiy to use SBXG's generated files.

**mkfs (ext3, vfat)**
  To generate the final image, mkfs (ext3 and vfat) will be required.

**curl and tar**
  To download compressed tarballs from the internet, and extract them. This is
  typically used to retrieve the toolchain and components to be built.

**swig**
  It seems that U-Boot requires swig to be built.

**autotools**
  SBXG will build from sources a package that uses the autotools. As such, the
  autotools programs needs to be installed (e.g. autoconf, automake, ...).
  This package is `genimage <https://github.com/pengutronix/genimage>`_.

**kernel build essentials**
  SBXG will compile the Linux Kernel and U-Boot. Hence, such a development
  environment shall be installed.

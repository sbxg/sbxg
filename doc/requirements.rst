SBXG Requirements
=================

**Python**
  SBXG relies on third-party tools to fulfull its duty. Its core is written
  with Python_. Python 2.7 will do, but it is advised to use Python 3.4 or
  later.

**Make**
  SBXG bootstraps its build system, by generating a Makefile. Therefore,
  ``make`` (only GNU make is tested) is a strong requirement for SBXG.

**Subcomponent**
  Subcomponent_ is used to fetch the components that SBXG depends on. It is
  packaged as a cargo crate, and therefore can be installed directly from
  cargo.

**mkfs (ext3, vfat)**
  To generate an image, mkfs (ext3 and vfat) will be required.

**autotools**
  SBXG will build from sources a package that uses the autotools. As such, the
  autotools programs needs to be installed (e.g. autoconf, automake, ...)

**kernel build essentials**
  SBXG will compile the Linux Kernel and U-Boot. Hence, such a development
  environment shall be installed.


Packages Installation
=====================

SBXG provides per GNU/Linux distribution scripts to install the necessary packages.
They are contained within the ``utils/`` directory, in the top source directory.
Run the script associated to your distribution.


.. _Python: https://www.python.org/
.. _Subcomponent: https://github.com/subcomponent/subcomponent

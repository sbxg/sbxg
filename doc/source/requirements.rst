SBXG Requirements
=================

**Python**
  SBXG relies on third-party tools to fulfull its duty. Its core is
  orchestrated with Python_. Python 2.7 will do, but it is advised to use
  Python 3.5 or later.

**Make**
  SBXG bootstraps its build system, by generating a Makefile. Therefore,
  ``make`` is a strong requirement for SBXG.

**Subcomponent**
  Subcomponent_ is used to fetch the components that SBXG depends on.
  It is packaged as a cargo crate, and therefore can be installed directly
  from cargo.

**mkfs (ext3, vfat)**
  To generate an image, mkfs (ext3 and vfat) will be required.

**autotools**
  SBXG will build from sources a package that uses the autotools. As such,
  the autotools programs needs to be installed (e.g. autoconf, automake, ...)

**kernel build essentials**
  SBXG will compile the Linux Kernel and U-Boot. Hence, such a development
  environment shall be installed.


Debian Packages
---------------

.. code:: bash

   apt install make python3
   cargo install subcomponent


.. _Python: https://www.python.org/
.. _genimage: https://git.pengutronix.de/cgit/genimage
.. _Subcomponent: https://github.com/subcomponent/subcomponent

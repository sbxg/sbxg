How Do I Do That?
=================

I want to compile a single component
------------------------------------

You first need to take a look at the files known to SBXG, by running the ``bootstrap.py``
script with the ``--show-library`` option:

.. code::

  $ ./bootstrap.py --show-library

  List of available boards (with variants):
    - cubietruck ( xen )
    - virtual ( vexpress-v7 )
    - orangepi-zero

  List of sources:
    - uboot: 2017.07
    - xen: 4.8.0
    - toolchain: local
    - toolchain: armv7-eabihf
    - kernel: linux-4.12.0
    - busybox: 1.27.1

  List of configurations:
    - bootscript: boot-sunxi-default
    - bootscript: boot-sunxi-xen
    - uboot: 2017.07-minimal
    - xen: 4.8-sunxi
    - kernel: linux-4.12-sunxi
    - kernel: linux-4.12-sunxi-xen-dom0
    - kernel: linux-4.12-xen-domu
    - busybox: minimal


I want to compile just a kernel
................................

From the list that is shown to you, you must pick:

* a kernel to be compiled (in the *List of sources*),
* a kernel configuration (in the *List of configurations*),
* a toolchain (in the *List of sources*).

Make sure that all parameters are coherent together. For instance, do not pick
a Xen configuration for a Linux kernel, or a Linux 3.4 configuration when you
are trying to build a Linux 4.14. Configurations are also linked to a given
architecture or SoC (e.g. cubietruck/sunxi), so make sure the toolchain you select
is coherent with the product you want to build.

For instance, if you want to cross-build a Linux 4.12.0 for a Cubietruck (sunxi):

.. code::

  bootstrap.py --kernel linux-4.12.0 linux-4.12-sunxi
               --toolchain armv7-eabihf


I want to compile just a bootloader
...................................

From the list that is shown to you, you must pick:

* a U-Boot to be compiled (in the *List of sources*),
* a U-Boot configuration (in the *List of configurations*),
* a toolchain (in the *List of sources*).


For instance, if you want to build a U-Boot 2017.07 locally (assuming an ARM
host):

.. code::

  bootstrap.py --uboot 2017.07 2017.07-minimal
               --toolchain local


I want to compile just Xen
..........................

From the list that is shown to you, you must pick:

* a Xen to be compiled (in the *List of sources*),
* a Xen configuration (in the *List of configurations*),
* a toolchain (in the *List of sources*).


For instance, if you want to cross-build a Xen 4.8.0 for a sunxi SoC:

.. code::

  bootstrap.py --xen 4.8.0 4.8-sunxi
               --toolchain armv7-eabihf



I want to generate a firmware image
------------------------------------

TODO :/

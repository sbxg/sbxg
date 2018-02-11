SBXG Configuration
==================

SBXG relies on two search paths that provide its configuration:

* the ``board`` search path and
* the ``lib`` search path.

These two concepts will be explained in further details in the following
sections. If no search path is specified, SBXG will assume the directories
``board/`` and ``lib/`` in the source source directory of SBXG.


Search Path
-----------

SBXG's configuration consist in a collection of structured files. These
structures reside in entries called the *search paths*.

If one needs to develop its own configuration, and wish to make it private
(outside of SBXG), it shall replicate the file hierarchy described in the
following sections, and set the search paths to the directorys containing this
new hierarchy.

The first *search path* is the **library**. It contains configurations files
that allow to retrieve and compile the various components that SBXG supports.

The second *search path* consists of **boards** configurations. These are files
that describe how several components shall be aggregate together to generate a
single firmware image. If you want to only build components without creating
a firmware image, you do not need this.

You can call the ``--show-lib`` option of the ``bootstrap.py`` script to print
the files that SBXG will look for. For example, from SBXG top source directory:

.. code::

  $ ./boostrap.py --show-lib
  List of available boards (with variants):
    - cubietruck ( xen )
    - virtual ( vexpress-v7 )
    - orangepi-zero

  List of sources:
    - uboot: 2017.07
    - xen: 4.8.2
    - toolchain: local
    - toolchain: armv7-eabihf
    - kernel: linux-4.14.8
    - kernel: linux-4.14.6
    - kernel: linux-4.14.17
    - kernel: linux-4.12.0
    - busybox: 1.27.1

  List of configurations:
    - bootscript: boot-sunxi-default
    - bootscript: boot-sunxi-xen
    - uboot: 2017.07-minimal
    - xen: 4.8-sunxi
    - kernel: linux-4.12-sunxi
    - kernel: linux-4.12-sunxi-xen-dom0
    - kernel: linux-4.14-sunxi-xen-dom0
    - kernel: linux-4.12-xen-domu
    - kernel: linux-4.14-xen-domu
    - busybox: minimal


When providing configuration or source files to SBXG, you will need to pass one
of these files.


SBXG's Board Directory
----------------------

First, let's start with an example:

.. code::

   boards/
   ├── cubietruck
   │   ├── board.yml
   │   ├── images
   │   │   └── default.j2
   │   └── xen.yml
   ├── orangepi-zero
   │   ├── board.yml
   │   └── images
   │       └── default.j2
   └── virtual
       ├── images
       │   └── guest.j2
       └── vexpress-v7.yml


Each subdirectory in ``boards/`` (which is the default directory searched by
SBXG) holds the configuration files for a given board. In our example, we have three
supported boards:

* Cubietruck_,
* OrangePiZero_,
* virtual (as a based to build virtual machines).

Within each of these directories ``board.yml`` is the default configuration
file that describes how different components are aggregated together. You may
want to have several configurations. These are called *variants* in SBXG's
terminology. An example is given by ``cubietruck/xen.yml``, which is an
alternative configuration to ``cubietruck/board.yml``. Notice the directories
``images/``. They contain genimage_ configuration and describe the layout of
the firmware image.


SBXG's Library Directory
------------------------

First, let's start with an example:

.. code::

   lib
   ├── configs
   │   ├── bootscripts
   │   │   ├── boot-sunxi-default.j2
   │   │   └── boot-sunxi-xen.j2
   │   ├── busybox
   │   │   └── minimal
   │   ├── kernel
   │   │   ├── linux-4.12-sunxi
   │   │   ├── linux-4.12-sunxi-xen-dom0
   │   │   ├── linux-4.12-xen-domu
   │   │   ├── linux-4.14-sunxi-xen-dom0
   │   │   └── linux-4.14-xen-domu
   │   ├── uboot
   │   │   └── 2017.07-minimal
   │   └── xen
   │       └── 4.8-sunxi
   └── sources
       ├── busybox
       │   └── 1.27.1.yml
       ├── kernel
       │   ├── linux-4.12.0.yml
       │   ├── linux-4.14.17.yml
       │   ├── linux-4.14.6.yml
       │   └── linux-4.14.8.yml
       ├── toolchain
       │   ├── armv7-eabihf.yml
       │   └── local.yml
       ├── uboot
       │   └── 2017.07.yml
       └── xen
           └── 4.8.2.yml

There are two directories within the library search path:

* ``sources/``: where configurations to fetch components reside:
  * ``busybox/``: to retrieve Busybox_
  * ``kernel/``: to retrive the principal kernel (e.g. Linux base or Xen Dom 0),
  * ``toolchain/``: to retrive the compilation toolchain,
  * ``uboot/``: to retrive the boot loader,
  * ``xen/``: to retrieve the Xen ARM hypervisor.
* ``configs/``: where configurations to compile components reside:
  * ``bootscripts/``: available boot scripts ,
  * ``busybox/``: per-Busybox version configurations,
  * ``kernel/``: per-Linux version configurations,
  * ``u-boot/``: per-U-boot version configurations,
  * ``xen/``: per-Xen version configurations.


.. _Cubietruck: https://linux-sunxi.org/Cubietruck
.. _OrangePiZero: http://linux-sunxi.org/Xunlong_Orange_Pi_Zero
.. _genimage: https://github.com/pengutronix/genimage
.. _Busybox: https://busybox.net

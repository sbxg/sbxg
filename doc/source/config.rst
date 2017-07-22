SBXG Configuration
==================

Search Path
-----------

SBXG's configuration consist in a collection of structured files. These
structures reside in an entity called the *search path*. If none is
provided, SBXG uses its top source directory as the search path.

If one needs to develop its own configuration, and wish to make it private
(outside of SBXG), it shall replicate the file hierarchy described in the
following sections, and set the search path to the directory containing this
new hierarchy.

To do so, one must call the ``bootstrap.py`` script with the option
``--search-path=<your/search/path>``.


Configurations File Hierarchy
-----------------------------

The following file hierarchy is an example that shows:

* an armv7 (with hardware floating point) toolchain,
* a Linux Kernel (4.12.0),
* a Xen Kernel (4.9.0),
* a U-Boot (2017.07),
* and a board named *cubietruck*.

.. code:: 

  .
  ├── boards
  │   └── cubietruck
  │       ├── board.yml
  │       ├── images
  │       │   ├── default.j2
  │       ├── kernel
  │       │   ├── linux-4.12-sunxi
  │       └── uboot
  │           ├── 2017.07-minimal
  │           └── boot-default.cmd
  ├── busybox
  │   └── 1.27.1.yml
  ├── kernels
  │   ├── linux-4.12.0.yml
  │   └── xen-4.9.0.yml
  ├── toolchains
  │   └── armv7-eabihf.yml
  └── uboot
      └── 2017.07.yml

 
When ``bootstrap.py`` is called with the ``--board=cubietruck`` option, the
configuration files in `boards/cubietruck/` will be used.


Toolchain Configuration
-----------------------

A toolchain configuration **must** reside in the `toolchains/` directory, and
is a yaml file that is defined as it follows:


.. code:: yaml

  extraction path of the toolchain:
    url: the download url of the toolchain
    compression: a list of compressions
    prefix: the toolchain prefix from the extraction path
    arch: the toolchain's architecture

It is possible to check the integrity of the toolchain archive by adding yaml
parameters such as `sha256` with the expected sha256. Upon download, the hash
will be checked to ensure that the toolchain retrieved has been correctly
retrieved.


U-Boot Configuration
--------------------

A U-Boot configuration **must** reside in the `uboot/` directory, and is a yaml
file that is defined as it follows:

.. code:: yaml

  extraction path of the U-Boot:
    url: the download url of the U-Boot 
    compression: a list of compressions

It is also possible to add a `sha256` key, but since U-Boot is distributed with
a PGP signature, it is better to make integrity checks with the PGP signature
distributed by U-Boot. You can use the keys `pgp_signature` and `pgp_pubkey` to
do handle the PGP signatures.

It is advised that the name of these configuration files be the version of
U-Boot, suffixed by the `yml` extension.


Kernel Configuration
--------------------

A kernel configuration **must** reside in the `kernels/` directory, and is a yaml
file that is defined as it follows:

.. code:: yaml

  extraction path of the kernel:
    url: the download url of the Kernel
    compression: a list of compressions

You can have the same integrity checks as the two components above. Note that the
configuration is used to generate subcomponent_ files.

The files are expected to be named: kernel type, dash, kernel version. For instance,
a Linux 4.12.1 configuration shall be named: `linux-4.12.1.yml`, whereas a Xen 4.8.0
configuration shall be named `xen-4.8.0.yml`.

Only `linux` and `xen` are handled for now.


.. _subcomponent: https://github.com/subcomponent/subcomponent



Busybox Configuration
---------------------

A busybox configuration **must** reside in the `busybox/` directory, and is a
yaml file that is defined as it follows:

.. code:: yaml

  extraction path of busybox :
    url: the download url of busybox 
    compression: a list of compressions


It is advised that the name of these configuration files be the version of
busybox, suffixed by the `yml` extension.

Board Configuration
-------------------

TODO

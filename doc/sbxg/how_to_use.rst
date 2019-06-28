How to use SBXG
===============================================================================

SBXG is distributed as a python package, with a pre-defined entry point. It
means you can use SBXG via its python API or as a command-line tool. N


Command-Line Interface
-------------------------------------------------------------------------------

.. admonition:: Stability of the CLI
   :class: warning

   Currently, SBXG's CLI is not stable. It means it can change at any
   time, without prior notice.


SBXG's command-line works with different **commands**:

* ``show``: to display information on SBXG's files;
* ``gen`` (or ``generate``): to generate a build system able to download and
  build various un-connected components that share the same toolchain.

Note that SBXG accepts the following arguments **before the commands**. They
will be applied to any command that follows:

* ``--color``: can be set to ``yes``, ``no`` or ``auto``, to respectively enable,
  disable or auto-detect if SBXG's output should contain colors.
* ``-I`` (or ``--lib-dir``): specify a directory to populate SBXG's components
  library. If no arguments are provided, SBXG's built-in library will be used.
  To understand what the library is, please refer to :doc:`/sbxg/library`.

sbxg show
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SBXG can display the contents of its library, which has been populated with the
``-I`` option. Take a look at :doc:`/sbxg/library` if you are unsure of what the
library is.

This command will display in a human-readable way on the standard output:

* what are the toolchains that are available;
* what are the linux, u-boot and xen sources available; and
* what are the linux, u-boot and xen configurations available.

Note that this command accepts the ``--mi`` option (for Machine Interface) that
displays the same information but serialized in JSON. This may come handy if
used for scripting. Refer to :doc:`/sbxg/mi` for details.

sbxg gen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``gen`` command can be invoked with the following parameters:

* ``-L`` (or ``--linux-source``): the **name** of a file describing how to
  retrieve the sources of a given version of the Linux kernel.
* ``-U`` (or ``--uboot-source``): the **name** of a file describing how to
  retrieve the sources of a given version of the U-Boot bootloader.
* ``-X`` (or ``--xen-source``): the **name** of a file describing how to
  retrieve the sources of a given version of the Xen hypervisor.
* ``-l`` (or ``--linux-config``) the **name** of a Kconfig file describing
  the various configuration parameters of a given Linux profile.
* ``-u`` (or ``--uboot-config``) the **name** of a Kconfig file describing
  the various configuration parameters of a given U-Boot profile.
* ``-x`` (or ``--xen-config``) the **name** of a Kconfig file describing
  the various configuration parameters of a given Xen profile.

The following argument pairs must be used together:

* ``-L`` and ``-l``;
* ``-U`` and ``-u``;
* ``-X`` and ``-x``.

Note that you can use as many arguments as you want. You can build a dozens of
Linux kernels in one go for example, as long as they are to be built with the
**same toolchain**.

A cross-compilation toolchain can be specified with the ``-t`` or
``--toolchain`` option. Note that if this option is not present, SBXG will
assume you are building **natively**.


.. admonition:: Architecture for cross-compilation
   :class: warning

   If you want to perform cross-compilation with the default toolchains, your
   host (the system that builds) MUST be x86. We don't provide toolchains that
   are not x86 binaries. You can however define your own toolchain.

It takes a **mandatory positional argument** that is the path to the directory
in which SBXG will generate its build system.


Python API
-------------------------------------------------------------------------------

.. admonition:: Stability of the Python API
   :class: warning

   Currently, SBXG's python API is not stable. It means it can change at any
   time, without prior notice.

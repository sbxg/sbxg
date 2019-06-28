Welcome to SBXG's documentation
===============================================================================

SBXG is a **build system generator** specialized in building from sources
low-level components that are the foundation of Linux-based embedded devices,
such as the
`U-Boot bootloader <https://www.denx.de/wiki/U-Boot>`_, the
`Linux kernel <https://www.kernel.org/>`_ and the
`Xen hypervisor <https://www.xenproject.org/>`_.

It is designed to offer a **high level of reproductibility and tracability**.
Given that the URLs pointing to the different components are always available,
SBXG should always generate the same outputs for a given set of inputs. No
surprise to be expected.

On top of being able to build just the low-level components, SBXG can generate
standalone images, ready to be flashed on an SDcard or used as virtual machine
disks. In this mode, SBXG expects the :doc:`rootfs </sbxg/rootfs>` to be
available, it does not generate one.

All components (but the cross-compilation toolchain) are built from source,
with a configuration file enforced by version. This allows SBXG users to rely
on the sources and their own (or pre-packaged) configurations, instead of a
black box downloaded from untrusted sources.

SBXG provides default configurations for some boards, toolchains, kernels and
u-boot, to demonstrate its capabilities, but one of its goal is to be able to
use opaque (private) user configurations that can leave outside of SBXG
(e.g. reside in a dedicated source control repository).


.. admonition:: Status of the project
   :class: warning

   SBXG is in **omega** stage (beyond alpha)! The documentation is being
   redacted, and some key features are being developed.

.. toctree::
   :caption: SBXG
   :maxdepth: 2

   sbxg/philosophy
   sbxg/install
   sbxg/how_to_use
   sbxg/rootfs

.. toctree::
   :caption: Tutorials
   :maxdepth: 2

   tutorials/use_builtin

.. toctree::
   :caption: Development
   :maxdepth: 2

   development/setup


.. _U-Boot: https://www.denx.de/wiki/U-Boot
.. _Linux: https://www.kernel.org/

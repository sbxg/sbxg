SBXG's documentation
====================

SBXG is a build system that generates bootable images for embedded devices.
The images generation is highly customizable, but is mainly composed of:

* a bootloader: U-Boot_,
* a kernel: Linux_,
* and a foreign root file system (e.g. generated with DFT_ or Debootstrap_).

All components but the toolchain are built from source, with a configuration
file enforced by version. This allows SBXG users to rely on the sources and
their own (or pre-packaged) configurations, instead of a black box downloaded
from untrusted sources.

SBXG provides default configurations for some boards, toolchains, kernels and
u-boot, to demonstrate its capabilities, but one of its goal is to be able to
use opaque (private) user configurations that can leave outside of SBXG
(e.g. reside in a dedicated source control repository).

This guide explains in details how to hack SBXG to develop your own
configurations, to forge system software for your embedded boards.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   requirements.rst
   startup.rst
   how-to.rst
   config.rst

.. _U-Boot: https://www.denx.de/wiki/U-Boot
.. _Linux: https://www.kernel.org/
.. _DFT: https://github.com/wbonnet/dft
.. _Debootstrap: https://wiki.debian.org/Debootstrap

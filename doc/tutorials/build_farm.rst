Tutorial: build farming
===============================================================================

Imagine that you want to compile multiple Linux kernels and U-Boot for
different embedded boards you want to setup. In this tutorial, we will consider
the `Cubietruck <http://cubieboard.org/tag/cubietruck/>` and the `Orange Pi
Zero <http://www.orangepi.org/orangepizero/>`.

Both of these platforms can be compiled using the same toolchain, and you want
to cross-compile on your x86 machine using the default ARM toolchain SBXG
provides.

It happens that you want to generate a finely tailored kernel for each of these
boards, and you want to do that because you know that SBXG provides these
configurations (you have already gone through :doc:`/tutorials/add_a_kernel`.
So, you will end up with the same Linux version for both targets, but different
configurations. Since you don't really care much about the bootloader, you
judge that both targets can share the same configuration.

So, to recapitulate, you want:

* a toolchain;
* one u-boot source;
* one u-boot configuration;
* one linux source;
* two linux configurations.

But now, which ones? And how do you tell SBXG to use that? That's actually
quite simple, run::

   sbxg show

and since you hayou will see something like::

  List of toolchains:
    - local
    - armv7-eabihf
  List of sources:
    - linux: linux-4.14.35
    - linux: linux-4.12.0
    - uboot: uboot-2017.07
    - xen: xen-4.8.3
  List of configurations:
    - linux: linux-4.12-sunxi
    - linux: linux-4.14-orange-pi-zero
    - linux: linux-4.14-cubietruck
    - uboot: uboot-2017.07-minimal
    - xen: xen-4.8-sunxi

Lucky 

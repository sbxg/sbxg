How about the rootfs?
===============================================================================

As explained in :doc:`the introduction </index>`, SBXG does not care about the
**Root Filesystem** (rootfs). The rootfs is completely out of the scope of
SBXG, because it is a completely different class of problem that requires
specialized tools, and a awful lot lot of community work. Luckily, we already
have tremendous work made openly available:

* `Buildroot <https://buildroot.org/>`_, to generate finely-tailored rootfs,
  mostly for embedded systems;
* `Debootstrap <https://wiki.debian.org/Debootstrap>`_, to retrieve pre-compiled
  Debian rootfs;
* `DFT <https://github.com/wbonnet/dft>`_, a tool to heavily customize Debian
  rootfs.
* `Gentoo stages <https://wiki.gentoo.org/wiki/Stage_tarball>`_, to generate or
  retrieve distribution-levels rootfs.
* And many, many more available choices...

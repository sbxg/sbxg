SBXG Core
=========

SBXG aims at producing software components for a dedicated embedded board
(e.g. [Cubietruck](http://www.cubietruck.com/),
      [Cubieboard](http://cubieboard.org/),
      [Raspberry PI(https://www.raspberrypi.org/)).
These include:
- a bootloader ([u-boot](http://www.denx.de/wiki/U-Boot));
- a kernel (only Linux is supported for now);
- a root file system (e.g. [Ubuntu](http://www.ubuntu.com/),
                           [Debian](https://www.debian.org/)).


Usage
=====

You must now _a priori_ the name of the board supported by SBXG.
You will find the exhaustive list at
https://github.com/sbxg/manifests/blob/master/README.md.

- Init the project with `make BOARD=<BOARD_NAME> init`. If you plan
  to use your own manifests, you can specify a custom URL by setting
  `MANIFESTS_URL`. This step will initialize repo.
- Sync the git repositories with `make sync`.
- Launch the build process: `make`.


You may want to split the build into pieces:
- bootloader: `make u-boot`;
- linux: `make linux`;
- rootfs: `make debootstrap`;
- image: `make prepare_sdcard`.


Contributors
============

Please refer to the `AUTHORS` file for an exhaustive list of the
contributors.

License
=======

SBXG is licensed under the **GNU General Public License version 3 (GPLv3)**.
For more details, please refer to the `COPYING` file.

SBXG Core
=========

[![Build Status](https://travis-ci.org/sbxg/sbxg.svg?branch=master)](https://travis-ci.org/sbxg/sbxg)

SBXG aims at producing software components for a dedicated embedded board
(e.g. [Cubietruck](http://www.cubietruck.com/),
      [Cubieboard](http://cubieboard.org/),
      [Raspberry PI(https://www.raspberrypi.org/)).
These include:
- a bootloader ([u-boot](http://www.denx.de/wiki/U-Boot));
- a kernel (only Linux is supported for now);
- a root file system (e.g. [Ubuntu](http://www.ubuntu.com/),
                           [Debian](https://www.debian.org/)).


Pre-requisites
--------------

You need to have installed the following tools:
- `git`;
- `sudo`;
- `repo`;
- `make`;
- `cmake`;
- `qemu` and `qemu-user-static`;
- `debootstrap`;
- `kpartx`;
- `libncurses`;
- `parted`;
- `binfmts`;
- `build-essential`.

The list of packages on a Debian distribution can be found in the file
`docker/Dockerfile`. For Ubuntu, please have a look at `.travis.yml`.


Usage
=====

SBXG's workflow is decomposed into several parts:

1. board configuration;
2. collecting the sources:
  1. (re-)initializing repo's internal state;
  2. fetching the sources;
3. configuring the kernel;
4. compiling the kernel;
5. compiling u-boot;
6. running `debootstrap` to generate a rootfs;
7. creating the image to be flashed on the equipment.


Basic Configuration
-------------------

SBXG relies on a configuration file named `.config`. It is generated by
the `mconf` tool, which is similar to the one used by the Linux kernel.

If you already have a configuration file, copy it as `.config`:
```bash
cp /path/to/your/config /path/to/sbxg/.config
```

If you don't (e.g. you are using SBXG for the first time or want to re-configure
a board), you need to run the setup **first**:

```bash
make menuconfig
```

The most important configuration step is to select your board. In the menu
`Board Selection` you need first to select the `Board Type`. Then, you
have to select a manifest file corresponding to the board you previously
selected in the menu `Manifest Selection`.

Please note that if you have your own manifest repository, you can
specify your git repository URL via the `MANIFESTS_URL` environment
variable:

```bash
make MANIFESTS_URL=https://git.mycompany.com/secret_manifests.git" menuconfig
```


Collecting Sources
------------------

After you hve **saved** before quitting the configuration menu, you are
ready to collect the sources from the manifest you have previously
selected. We use [repo](http://source.android.com/source/using-repo.html)
to do that. Make sure it is installed first! Then run:

```bash
make init
```

This will intialize repo's internal state. Then make repo fetch all the
sources with:

```bash
make sync
```

Since repo will fetch the kernel sources, u-boot sources and various
components, this might take a while depending on your bandwidth and
the servers'.


Running the Workflow
--------------------

At this point, if you just want to build from the exising configuration,
just run:

```bash
make
```

And boom, done!



Build Steps
===========

You may want to create your own configurations, run parts of the build, etc.
This section was made for you!


Kernel Build
------------

For now, only Linux is supported. But SBXG has been thought to be extended to
any Kernel.

You can alterate the kernel's configuration as you wish. You can copy your
own configuration to the kernel directory by using the command:

```bash
make KERNEL_CONFIG="/path/to/your/config" linux-config
```

To run a `make` target within Linux, run:

```bash
make linux-<YOUR_TARGET>
```

Compile the kernel with:

```bash
make linux
```


Bootloader (U-Boot)
-------------------

To run a `make` target within U-Boot, run:

```bash
make u-boot-<YOUR_TARGET>
```

Compile U-Boot with:

```bash
make u-boot
```


Generating the rootfs
---------------------

Run:

```bash
make debootstrap
```

Creating the image
------------------

Run:
```bash
make prepare_sdcard
```


Contributors
============

Please refer to the `AUTHORS` file for an exhaustive list of the
contributors.

License
=======

SBXG is licensed under the **GNU General Public License version 3 (GPLv3)**.
For more details, please refer to the `COPYING` file.

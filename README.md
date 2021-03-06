# SBXG

SBXG is a specialized build system generator that allows the generation of
bootable images for embedded devices, or the compliation of individual
components of those images. The images generation is highly customizable, annd
is mainly composed of:
- a bootloader: [U-Boot][1],
- a kernel: [Linux][2], [Xen][13],
- and a foreign root file system.

## Model

All the components (but the foreign root file system) are built from source,
using versioned configuration files (i.e. Linux/U-Boot/Xen/Busybox Kconfig
products).  This allows SBXG users to rely on the sources and their own (or
pre-packaged) configurations, instead of a black box downloaded from untrusted
sources.

SBXG provides default configurations for some boards, toolchains, kernels and
u-boot, to demonstrate its capabilities, but one of its goal is to be able to
use opaque (private) user configurations, that may not be included in the open
source version of SBXG.


## Supported Components

The following list shows the built-in components shipped with SBXG, to
demonstrate its capabilities. It is trivial to add more.

- Embedded Boards:
  - [Cubietruck][3]
  - [Orange Pi Zero][6]
- Kernels:
  - [Linux][2]
  - [Xen][13]
- Bootloaders:
  - [U-Boot][1]
- Initramfs:
  - [Busybox][11]
- Toolchains:
  - [Arm-v7 eabihf][12]


To see more of the supported components, run the `bootstrap.py` script with the
`--show-library` option. This will display the exact list of the supported
boards, sources and configurations. You can add the `--no-color` if you find the
output too flashy or if you want to manipulate the output by another program:

```bash
./bootstrap.py --show-library
./bootstrap.py --show-library --no-color
```


## Pre-requisites

SBXG relies on third-party tools to fulfill its duty:
- `git`, to retrieve [genimage][4]'s sources,
- `python` (at least 3.4),
- the python packages `jinja` and `pyaml`,
- `make`,
- `mkfs` (ext3, vfat),
- `build-essential` tools (to compile the kernel and u-boot),
- autotools programs (such as autoreconf, autoconf, ...) needed to compile
  genimage.
- [subcomponent][5], which is a rust tool to download the components. It is
  a packaged cargo crate, and therefore can be installed from cargo
  (`cargo install subcomponent`).

To make installation of these dependencies easier, scripts are made available
in the `utils/` directory. Select the one that matches your distribution, and
run it as a normal user (no sudo). Python and rust packages will be locally
installed, while packages will ask for the admin password.


```bash
./utils/install_debian_packages.sh # For Debian/Ubuntu/...
./utils/install_gentoo_packages.sh # For Gentoo
```

You may be asked to run by yourself additional commands, that cannot be safely
executed by these scripts, such as changing your environment variables.


## Usage

You first must **bootstrap** SBXG as we generate its build system. First,
create a build directory, somewhere on your filesystem, where you will have RWX
access. SBXG enforces that the source directory (the downloaded sources) must
be kept clean. Hence, you cannot generate files directly from the source
directory. You can, however, create a specific directory (i.e. `build/`) in the
sources, from which you can bootstrap SBXG:

```bash
mkdir -p build && cd build
```

If you don't have a rootfs ready to be flashed, and if you happen to have the
`debootstrap` command available on your system, SBXG provides a small script
that will create a minimal Debian stable rootfs just for you. From the build
directory you just created, run:

```bash
sudo ../scripts/create-debootstrap.sh
```

This will take some time (and requires privileges), as debootstrap takes some
time to retrieve and configure the minimal Debian rootfs. Note that you will
need to have `qemu-system` and `qemu-user-static` installed.


Once you are done, you can bootstrap SBXG by calling `bootstrap.py`:

```bash
../bootstrap.py --board cubietruck
```

In the example above, the system has been bootstrapped for the [Cubietruck][3]
board. `bootstrap.py` provides a lot of options that are available by calling
the script with the `--help` option.

Once the bootstrapping is complete, you will see a lot of new files in your
build directory. You should not directly manipulate them, but nothing prevents
you from doing it. Be aware that running `bootstrap.py` again will re-write the
files, and modifications will be lost! You also should refrain yourself from
modifying the downloaded sources (especially the sources of genimage, which
come from a git repository), as `subcomponent` will complain if the sources
are not what it expects.

You can run `make help` to see the available targets. When you are ready, just
run `make` or `make all` to generate your image. You may want to use the `-j`
option to parallelize the build, but since three components will be built
in parallel, expect your stdout to be messed up.

You will find your final image in `images/`. You are then free to flash it
with things like `dd`.

## Documentation

More documentation is available in the `doc/` directory. It can be nicely
generated by [sphinx][7]. If you have `sphinx` installed, you can build the
documentation by running `make -C doc html`. The html documentation will be
available in `doc/build/html/`.

## Contributors

Please refer to the `AUTHORS` file for an exhaustive list of the contributors.

## License

SBXG is licensed under the **MIT** license. For details, please refer to the
`LICENSE` file.

[1]: https://www.denx.de/wiki/U-Boot
[2]: https://www.kernel.org/
[3]: https://linux-sunxi.org/Cubietruck
[4]: https://git.pengutronix.de/cgit/genimage
[5]: https://github.com/subcomponent/subcomponent
[6]: http://www.orangepi.org/orangepizero/
[7]: http://www.sphinx-doc.org/en/stable/
[10]: https://www.denx.de/wiki/U-Boot/WebHome
[11]: https://busybox.net/
[12]: http://toolchains.free-electrons.com/
[13]: https://www.xenproject.org/

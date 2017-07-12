# SBXG

SBXG is a build system that generates bootable images for embedded devices.
The images generation is highly customizable, but is mainly composed of:
- a bootloader: [U-Boot][1],
- a kernel: [Linux][2],
- and a foreign root file system.

## Model

The bootloader and the kernel are built from source, with a configuration file
enforced by version. This allows SBXG users to rely on the sources and their
own (or a pre-packaged) configurations, instead of a black box downloaded from
untrusted sources.

SBXG provides default configurations for some boards, toolchains, kernels and
u-boot, to demonstrate its capabilities, but one of its goal is to be able to
use opaque (private) user configurations.


## Supported Boards

- [Cubietruck][3]



## Pre-requisites

SBXG relies on third-party tools to fulfill its duty:
- `git`, to retrieve [genimage][4]'s sources,
- `python` (2.7 or 3.5),
- `make`,
- `mkfs` (ext3, vfat),
- `build-essential` tools (to compile the kernel and u-boot),
- autotools programs (such as autoreconf, autoconf, ...) needed to compile
  genimage.
- [subcomponent][5], which is a rust tool to download the components. 
  Subcomponent is currently not packaged, you will have to compile it from
  sources, and install it on your system (`cargo install`).
 


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


Once you have created the build directory and make it your current working directory,
you can bootstrap SBXG by calling `bootstrap.py`:

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

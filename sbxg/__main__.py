# Copyright (c) 2017, 2019 Jean Guyomarc'h
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import os
import shutil
import sys
from pathlib import Path

import sbxg
from sbxg.utils import ANSI_STYLE
from sbxg import error as E


def show_library(board_dirs, lib_dirs):
    """
    Dump the board and lib path's contents.
    """

    # First, go through the board directories to see the boards that
    # are available.
    print("List of available boards (with variants):")
    for board_dir in board_dirs:
        # Boards are directories that reside directly with a board dir
        boards = os.listdir(board_dir)
        for board in boards:
            print("  - {}{}{}".format(
                ANSI_STYLE['okblue'], board,  ANSI_STYLE['endc']
            ), end='')
            # Search with the board directory for variants. Variants are
            # .yml files, and exclude board.yml.
            file_list = os.listdir(os.path.join(board_dir, board))
            variants = []
            for variant in file_list:
                if variant.endswith(".yml") and variant != "board.yml":
                    variants.append(os.path.splitext(variant)[0])
            if len(variants) > 0:
                print(' (', end='')
                for variant in variants:
                    print(" {}{}{}".format(ANSI_STYLE['okgreen'], variant,
                                           ANSI_STYLE['endc']), end='')
                print(' )')
            else:
                print("")

    # Then, grab the list of sources, for each lib dir in the lib path.
    # We will search in the sources directory with these paths.
    print("\nList of sources:")
    for lib_dir in lib_dirs:
        for root, _, files in os.walk(os.path.join(lib_dir, "sources")):
            for item in files:
                # We search for .yml files only
                if item.endswith('.yml'):
                    item_type = os.path.basename(root)
                    item = os.path.splitext(item)[0]
                    print("  - {}{}{}: {}{}{}".format(
                        ANSI_STYLE['okblue'], item_type, ANSI_STYLE['endc'],
                        ANSI_STYLE['okgreen'], item, ANSI_STYLE['endc'],
                    ))

    print("\nList of toolchans:")
    for lib_dir in lib_dirs:
        for root, _, files in os.walk(os.path.join(lib_dir, "toolchains")):
            for item in files:
                # We search for .yml files only
                if item.endswith('.yml'):
                    item_type = os.path.basename(root)
                    item = os.path.splitext(item)[0]
                    print("  - {}{}{}".format(
                        ANSI_STYLE['okgreen'], item, ANSI_STYLE['endc'],
                    ))

    # And finally, do the same for configurations.
    print("\nList of configurations:")
    for lib_dir in lib_dirs:
        for root, _, files in os.walk(os.path.join(lib_dir, "configs")):
            for item in files:
                # We search for .yml files only
                if os.path.isfile(os.path.join(root, item)):
                    item_type = os.path.basename(root)
                    # Remove the "s" to "bootscripts" for pretty print
                    if item_type == "bootscripts":
                        item_type = "bootscript"
                    # Remove the .j2 extensions
                    if item.endswith(".j2"):
                        item = os.path.splitext(item)[0]
                    print("  - {}{}{}: {}{}{}".format(
                        ANSI_STYLE['okblue'], item_type, ANSI_STYLE['endc'],
                        ANSI_STYLE['okgreen'], item, ANSI_STYLE['endc'],
                    ))

def install_rootfs(rootfs, dest):
    if os.path.isfile(rootfs):
        shutil.copy(rootfs, dest)
    else:
        raise E.SbxgError("Rootfs file '{}' does not exist".format(rootfs))

class Help:
    CHDIR = 'Go to the specified directory before doing anything'
    KERNEL_SOURCE = "Name of the kernel source file"
    KERNEL_CONFIG = "Name of the kernel configuration file"
    XEN_SOURCE = "Name of the Xen source file"
    XEN_CONFIG = "Name of the Xen configuration file"
    UBOOT_SOURCE = "Name of the U-Boot source file"
    UBOOT_CONFIG = "Name of the U-Boot configuration file"
    TOOLCHAIN = "specify a toolchain to be used outside of the board execution"
    COLOR = "Turn on or off the console output"
    SHOW_LIB = "Prints in stdout the library of available components and exits"
    LIB_DIR = """Add a directory to the library search path. When this argument
        is not specified, the lib/ directory of SBXG will be used"""

def getopts(argv):
    parser = argparse.ArgumentParser(description='SBXG Boostrapper')

    parser.add_argument("--directory", "-C", metavar='DIR', help=Help.CHDIR)
    parser.add_argument("--color", choices=["yes", "no", "auto"],
                        default="auto", help=Help.COLOR)
    parser.add_argument('--kernel-source', '-K', metavar='KERNEL_SOURCE',
                        help=Help.KERNEL_SOURCE)
    parser.add_argument('--kernel-config', '-k', metavar='KERNEL_CONFIG',
                        help=Help.KERNEL_CONFIG)
    parser.add_argument('--xen-source', '-X', metavar='XEN_SOURCE',
                        help=Help.XEN_SOURCE)
    parser.add_argument('--xen-config', '-x', metavar='XEN_CONFIG',
                        help=Help.XEN_CONFIG)
    parser.add_argument('--uboot-source', '-U', metavar='UBOOT_SOURCE',
                        help=Help.UBOOT_SOURCE)
    parser.add_argument('--uboot-config', '-u', metavar='UBOOT_CONFIG',
                        help=Help.UBOOT_CONFIG)
    parser.add_argument('--toolchain',  '-t', metavar='TOOLCHAIN',
                        default='local', help=Help.TOOLCHAIN)
    parser.add_argument('--lib-dir', '-L', nargs='+', metavar="LIB_DIR",
                        help=Help.LIB_DIR)
    parser.add_argument('--show-library', action='store_true',
                        help=Help.SHOW_LIB)
    args = parser.parse_args(argv[1:])

    def _component_args_check(opt_cfg, opt_source):
        # Source Config
        #    0     0      OK
        #    0     1      FAIL
        #    1     0      FAIL
        #    1     1      OK
        src = getattr(args, opt_source.replace('-', '_'))
        cfg = getattr(args, opt_cfg.replace('-', '_'))
        if bool(src) != bool(cfg):
            raise E.SbxgError(f"Options --{opt_cfg} and "
                              f"--{opt_source} must be used together")

    for component in ('kernel', 'uboot', 'xen'):
        _component_args_check(f"{component}-source", f"{component}-config")

    # If we required no colors to be printed out, unset the ANSI codes that
    # were provided.
    #if args.no_color:
    #    for key in ANSI_STYLE:
    #        ANSI_STYLE[key] = ''

    # If --board-variant is used, --board must have been specified
    #if args.board_variant and not args.board:
    #    raise E.SbxgError("--board-variant cannot be used without --board")
    #if args.kernel and args.board:
    #    raise E.SbxgError("--kernel and --board cannot be used together")
    #if args.xen and args.board:
    #    raise E.SbxgError("--xen and --board cannot be used together")
    #if args.uboot and args.board:
    #    raise E.SbxgError("--uboot and --board cannot be used together")

    #if not args.board and not args.kernel and not args.uboot and not args.xen \
    #        and not args.show_library:
    #    raise E.SbxgError("At least one of the following option is expected: "
    #                      "--board, --kernel, --uboot, --xen")

    return args


def main(argv):
    args = getopts(argv)
    if args.directory:
        os.chdir(args.directory)

    # The top source directory is where this script resides, whereas the build
    # directory is where this script was called from.
    top_src_dir = Path(__file__).resolve().parent.parent
    top_build_dir = Path.cwd().resolve()

    ## The default board directory search path is boards/
    #if not args.board_dir:
    #    args.board_dir = [top_src_dir / "boards"]

    # The default lib directory search path is lib/
    if not args.lib_dir:
        args.lib_dir = [top_src_dir / "lib"]

    # Dump the library, and exit with success
    if args.show_library:
        #show_library(args.board_dir, args.lib_dir)
        show_library([], args.lib_dir)
        sys.exit(0)

    # Initialize the templates directory to the one contained within SBXG
    template_dirs = [top_src_dir / "templates"]
    components = []

    # I forbid you to use the source directory as the build directory!
    if top_src_dir == top_build_dir:
        raise E.SbxgError("Run bootstrap.py from a build directory that is "
                        "distinct from the source directory.")
        sys.exit(1)

    # The lib dirs provide a template path. We must add them!
    for lib_dir in args.lib_dir:
        bootscript_path = Path(lib_dir) / "configs" / "bootscripts"
        if bootscript_path.exists():
            template_dirs.append(bootscript_path)

    # The main database that will hold our configuration
    database = sbxg.model.Database(top_src_dir, top_build_dir)

    toolchain = sbxg.utils.get_toolchain(args.lib_dir, args.toolchain)
    database.set_toolchain(toolchain)

    #if args.board:
    #    # Select the configuration file for the previously selected board. It
    #    # is either 'board.yml' for the default configuration, or another yaml
    #    # file if a variant is provided. Fail if the configuration file does
    #    # not exist.
    #    config, board_dir = sbxg.utils.get_board_config(
    #        args.board_dir,
    #        args.board,
    #        args.board_variant if args.board_variant else 'board'
    #    )
    #    board = sbxg.model.Board(config, toolchain)
    #    board.load(args.lib_dir, board_dir)
    #    database.set_board(board)
    #    # Copy the rootfs to the input path of genimage
    #    components.extend(['kernel', 'genimage'])
    #    if not board.vm:
    #        components.append('uboot')
    #    template_dirs.append(board_dir / 'images')
    #    if board.xen:
    #        components.append('xen')

    if args.kernel_source:
        source = sbxg.utils.get_kernel_source(args.lib_dir, args.kernel_source)
        config = sbxg.utils.get_kernel_config(args.lib_dir, args.kernel_config)
        database.set_kernel(source, config)

    if args.uboot_source:
        source = sbxg.utils.get_uboot_source(args.lib_dir, args.uboot_source)
        config = sbxg.utils.get_uboot_config(args.lib_dir, args.uboot_config)
        database.set_uboot(source, config)

    if args.xen_source:
        source = sbxg.utils.get_xen_source(args.lib_dir, args.xen_source)
        config = sbxg.utils.get_xen_config(args.lib_dir, args.xen_config)
        database.set_xen(source, config)


    # Now that we are done collecting the data from the configurations, and we
    # have fed our data model, initialize the templating engine.
    templater = sbxg.template.Templater(database.context(), template_dirs)
    print(database.context())

    ## If we are to use genimage, create right now the directories that genimage
    ## will need.
    #if database.genimage:
    #    keys = ['build_dir', 'output_path', 'input_path', 'root_path', 'tmp_path']
    #    for key in keys:
    #        gen_dir = database.genimage[key]
    #        if not gen_dir.exists():
    #            os.makedirs(gen_dir)
    #    genimage_in = database.genimage['input_path']
    #    if database.board:
    #        install_rootfs(database.board.rootfs, genimage_in)

    #if database.board:
    #    # Generate the boot script from a template, if one was specified. This
    #    # generated bootscript will just be a templated file. When dealing with
    #    # U-Boot bootscript, the generated makefile will create the final
    #    # boot script with tools like mkimage.
    #    boot_cmd = top_build_dir / database.board.templated_boot_script_name
    #    if not database.board.vm:
    #        templater.template_file(database.board.boot_script, boot_cmd)

    #    # And finally generate the genimage configuration
    #    templater.template_file(
    #        os.path.basename(database.board.image),
    #        database.genimage['config']
    #    )

    # Generate the makefile, which will control the build system
    templater.template_file("Makefile.j2", top_build_dir / "Makefile")

if __name__ == "__main__":
    main(sys.argv)

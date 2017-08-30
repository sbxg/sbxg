#! /usr/bin/env python
#
# Copyright (c) 2017 Jean Guyomarc'h
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
import sys
import traceback

import sbxg
from sbxg import error as E


# This is derivated from https://stackoverflow.com/a/287944
# I don't want to use a module just for color, as this is an extra dependency
# that adds more failure paths. SBXG will only run on Linux anyway, as we are
# compiling U-Boot and Linux. We can still stop echoing colors on demand.
ANSI_STYLE = {
    'header': '\033[95m',
    'okblue': '\033[94m',
    'okgreen': '\033[92m',
    'warning': '\033[93m',
    'fail': '\033[91m',
    'endc': '\033[0m',
    'bold': '\033[1m',
    'underline': '\033[4m',
}

def error(message):
    print("{}error:{} {}".format(
        ANSI_STYLE['fail'],
        ANSI_STYLE['endc'],
        message,
    ), file=sys.stderr)


def getopts(argv):
    parser = argparse.ArgumentParser(description='SBXG Boostrapper')
    parser.add_argument(
        '--subcomponent', type=str, default='subcomponent',
        help='Provide the path to the subcomponent program'
    )
    parser.add_argument(
        '--no-download', '-n', action='store_true',
        help="Don't make subcomponent download the components"
    )
    parser.add_argument(
        '--no-color', action='store_true',
        help='Disable colored output when this option is specified'
    )
    parser.add_argument(
        '--kernel', nargs=2, metavar='FILE',
        help="""specifying this option makes SBXG to only build a kernel.
        Xen does not fall under this category.
        A toolchain must be specified"""
    )
    parser.add_argument(
        '--xen', nargs=2, metavar='FILE',
        help="""specifying this option makes SBXG to only build a Xen kernel.
        A toolchain must be specified"""
    )
    parser.add_argument(
        '--uboot', nargs=2, metavar='FILE',
        help="""specifying this option makes SBXG to only build U-Boot.
        A toolchain must be specified"""
    )
    parser.add_argument(
        '--toolchain', type=str, metavar='TOOLCHAIN',
        help="""specify a toolchain to be used outside of the board execution.
        This option must be specified when building a component on demand."""
    )
    parser.add_argument(
        '--board', '-B', type=str,
        help="""Name of an SBXG board that reside within a directory specified
         by the --board-dir arguments"""
    )
    parser.add_argument(
        '--board-variant', '-b', type=str,
        help="""Name of a variant configuration for a selected board. If none
        is provided, a default configuration will be used"""
    )
    parser.add_argument(
        '--board-dir', nargs='+',
        help="""Add a directory to the boards search path. When this argument
        is not specified, the boards/ directory of SBXG will be used"""
    )
    parser.add_argument(
        '--lib-dir', '-L', nargs='+',
        help="""Add a directory to the library search path. When this argument
        is not specified, the lib/ directory of SBXG will be used"""
    )
    args = parser.parse_args(argv[1:])

    # If --board-variant is used, --board must have been specified
    if args.board and not args.toolchain:
        raise E.SbxgError("--board requires the use of --toolchain")
    if args.board_variant and not args.board:
        raise E.SbxgError("--board-variant cannot be used without --board")
    if args.kernel and args.board:
        raise E.SbxgError("--kernel and --board cannot be used together")
    if args.xen and args.board:
        raise E.SbxgError("--xen and --board cannot be used together")
    if args.uboot and args.board:
        raise E.SbxgError("--uboot and --board cannot be used together")
    if args.kernel and not args.toolchain:
        raise E.SbxgError("--kernel requires the use of --toolchain")
    if args.uboot and not args.toolchain:
        raise E.SbxgError("--uboot requires the use of --toolchain")
    if args.xen and not args.toolchain:
        raise E.SbxgError("--xen requires the use of --toolchain")

    if not args.board and not args.kernel and not args.uboot and not args.xen:
        raise E.SbxgError("At least one of the following option is expected: "
                          "--board, --kernel, --uboot, --xen")

    return args


def main(argv):
    args = getopts(argv)

    # If we required no colors to be printed out, unset the ANSI codes that
    # were provided.
    if args.no_color:
        for key in ANSI_STYLE:
            ANSI_STYLE[key] = ''


    # The top source directory is where this script resides, whereas the build
    # directory is where this script was called from.
    top_src_dir = os.path.dirname(os.path.realpath(__file__))
    top_build_dir = os.getcwd()

    # Initialize the templates directory to the one contained within SBXG
    template_dirs = [os.path.join(top_src_dir, "templates")]
    components = []

    # I forbid you to use the source directory as the build directory!
    if os.path.normpath(top_src_dir) == os.path.normpath(top_build_dir):
        error("Run bootstrap.py from a build directory that is "
              "distinct from the source directory.")
        sys.exit(1)

    # The default board directory search path is boards/
    if not args.board_dir:
        args.board_dir = [os.path.join(top_src_dir, "boards")]

    # The default lib directory search path is lib/
    if not args.lib_dir:
        args.lib_dir = [os.path.join(top_src_dir, "lib")]

    # The lib dirs provide a template path. We must add them!
    for lib_dir in args.lib_dir:
        bootscript_path = os.path.join(lib_dir, "configs", "bootscripts")
        if os.path.exists(bootscript_path):
            template_dirs.append(bootscript_path)

    # The main database that will hold our configuration
    database = sbxg.model.Database(top_src_dir, top_build_dir)

    if args.toolchain:
        args.toolchain = sbxg.utils.get_toolchain(
            args.lib_dir, args.toolchain
        )
        local_toolchain = False
        if os.path.basename(args.toolchain) == "local.yml":
            local_toolchain = True

        toolchain = sbxg.model.Toolchain(args.toolchain, local_toolchain)
        toolchain.load()
        database.set_toolchain(toolchain)
        if not local_toolchain:
            components.append('toolchain')

    if args.board:
        # Select the configuration file for the previously selected board. It
        # is either 'board.yml' for the default configuration, or another yaml
        # file if a variant is provided. Fail if the configuration file does
        # not exist.
        config, board_dir = sbxg.utils.get_board_config(
            args.board_dir,
            args.board,
            args.board_variant if args.board_variant else 'board'
        )
        board = sbxg.model.Board(config, toolchain)
        board.load(args.lib_dir, board_dir)
        database.set_board(board)
        components.extend(['kernel', 'uboot', 'genimage'])
        template_dirs.append(os.path.join(board_dir, 'images'))
        if board.xen:
            components.append('xen')

    if args.kernel:
        args.kernel[0] = sbxg.utils.get_kernel_source(
            args.lib_dir, args.kernel[0]
        )
        args.kernel[1] = sbxg.utils.get_kernel_config(
            args.lib_dir, args.kernel[1]
        )
        kernel_source = sbxg.model.Kernel(args.kernel[0])
        kernel_source.load()
        kernel_config = args.kernel[1]
        database.set_kernel(kernel_source, kernel_config)
        components.append('kernel')

    if args.uboot:
        args.uboot[0] = sbxg.utils.get_uboot_source(
            args.lib_dir, args.uboot[0]
        )
        args.uboot[1] = sbxg.utils.get_uboot_config(
            args.lib_dir, args.uboot[1]
        )
        uboot_source = sbxg.model.Uboot(args.uboot[0])
        uboot_source.load()
        uboot_config = args.uboot[1]
        database.set_uboot(uboot_source, uboot_config)
        components.append('uboot')

    if args.xen:
        args.xen[0] = sbxg.utils.get_xen_source(
            args.lib_dir, args.xen[0]
        )
        args.xen[1] = sbxg.utils.get_xen_config(
            args.lib_dir, args.xen[1]
        )
        xen_source = sbxg.model.Xen(args.xen[0])
        xen_source.load()
        xen_config = args.xen[1]
        database.set_xen(xen_source, xen_config)
        components.append('xen')

    # Now that we are done collecting the data from the configurations, and we
    # have fed our data model, initialize the templating engine.
    templater = sbxg.template.Templater(database, template_dirs)

    # Fetch the required components
    subcomponent = sbxg.subcomponent.Subcomponent(templater, args.subcomponent)
    subcomponent.add_components(components)
    subcomponent.call(top_build_dir, no_download=args.no_download)

    # If we are to use genimage, create right now the directories that genimage
    # will need.
    if database.genimage:
        keys = ['build_dir', 'output_path', 'input_path', 'root_path', 'tmp_path']
        for key in keys:
            gen_dir = database.genimage[key]
            if not os.path.exists(gen_dir):
                os.makedirs(gen_dir)
        if database.guests:
            for guest in database.guests:
                input_dir = os.path.join(database.genimage['input_path'],
                                         "guest{}".format(guest.guest_id))
                if not os.path.exists(input_dir):
                    os.makedirs(input_dir)

    if database.board:
        # Generate the boot script from a template, if one was specified. This
        # generated bootscript will just be a templated file. When dealing with
        # U-Boot bootscript, the generated makefile will create the final
        # boot script with tools like mkimage.
        boot_cmd = os.path.join(
            top_build_dir,
            database.board.templated_boot_script_name
        )
        templater.template_file(
            database.board.boot_script,
            boot_cmd
        )

        # And finally generate the genimage configuration
        templater.template_file(
            os.path.basename(database.board.image),
            database.genimage['config']
        )

        # Generate genimage configurations for each registered guest
        if database.guests:
            for guest in database.guests:
                templater.template_file(
                    os.path.basename(guest.image),
                    os.path.join(top_build_dir, guest.genimage_config)
                )

    # Generate the makefile, which will control the build system
    templater.template_file(
        "Makefile.j2", os.path.join(top_build_dir, "Makefile")
    )


# Run the main entry point. We will also catch all the exceptions to
# pretty-format the reason of failure.
if __name__ == "__main__":
    try:
        main(sys.argv)
    except sbxg.error.SbxgError as exception:
        # SBXG will raise its own errors through custom exceptions. They are
        # already well-formated, and correspond to nominal failures.
        error(exception)
        sys.exit(1)
    except Exception:
        # Generale exceptions are the one not planned by SBXG.
        error("Unhandled error! Please report the following trace:")
        traceback.print_exc(file=sys.stderr)
        error("Aborting!")
        sys.exit(127)

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
import json
import os
import sys
from pathlib import Path

import sbxg
from sbxg.utils import ANSI_STYLE
from sbxg import error as E

def _init_top_build_dir(directory):
    top_build_dir = Path(directory).resolve()
    # Create the output directory if it does not exist
    Path.mkdir(top_build_dir, parents=True, exist_ok=True)
    return top_build_dir

def _cmd_show(args, top_src_dir):
    lib = sbxg.library.get(args.lib_dir)
    if args.mi:
        print(json.dumps(lib))
    else:
        end = ANSI_STYLE['endc']
        stype = ANSI_STYLE['okblue']
        sname = ANSI_STYLE['okgreen']

        print("List of toolchains:")
        for toolchain in lib["toolchains"]:
            print(f"  - {sname}{toolchain['name']}{end}")

        print("List of sources:")
        for source in lib["sources"]:
            print(f"  - {stype}{source['type']}{end}:",
                  f"{sname}{source['name']}{end}")

        print("List of configurations:")
        for config in lib["configurations"]:
            print(f"  - {stype}{config['type']}{end}:",
                  f"{sname}{config['name']}{end}")


def _cmd_gen(args, top_src_dir):
    top_build_dir = _init_top_build_dir(args.outdir)

    # The main database that will hold our configuration
    database = sbxg.model.Database(top_src_dir, top_build_dir)

    toolchain = sbxg.utils.get_toolchain(args.lib_dir, args.toolchain)
    database.set_toolchain(toolchain)

    for src, cfg in zip(args.linux_source, args.linux_config):
        source = sbxg.utils.get_linux_source(args.lib_dir, src)
        config = sbxg.utils.get_linux_config(args.lib_dir, cfg)
        database.add_linux(source, config)

    for src, cfg in zip(args.uboot_source, args.uboot_config):
        source = sbxg.utils.get_uboot_source(args.lib_dir, src)
        config = sbxg.utils.get_uboot_config(args.lib_dir, cfg)
        database.add_uboot(source, config)

    for src, cfg in zip(args.xen_source, args.xen_config):
        source = sbxg.utils.get_xen_source(args.lib_dir, src)
        config = sbxg.utils.get_xen_config(args.lib_dir, cfg)
        database.add_xen(source, config)

    # Now that we are done collecting the data from the configurations, and we
    # have fed our data model, initialize the templating engine.
    template_dirs = [top_src_dir / "templates"]
    templater = sbxg.template.Templater(database.context(), template_dirs)
    templater.template_file("Makefile.j2", top_build_dir / "Makefile")


def _cmd_board(args, top_src_dir):
    top_build_dir = _init_top_build_dir(args.outdir)

    # The main database that will hold our configuration
    database = sbxg.model.Database(top_src_dir, top_build_dir)

    config = sbxg.utils.get_board_config(args.board_dir, args.board)

    # Now that we are done collecting the data from the configurations, and we
    # have fed our data model, initialize the templating engine.
    #template_dirs = [Path(board_dir, "bootscripts"),
    #                 Path(board_dir, "images") for board_dir in args.board_dir]
    #template_dirs.append(top_src_dir / "templates")
    #templater = sbxg.template.Templater(database.context(), template_dirs)
    #templater.template_file("Makefile.j2", top_build_dir / "Makefile")




class Help:
    OUTDIR = 'Path to the directory in which files should be generated'
    LINUX_SOURCE = "Name of the Linux source file"
    LINUX_CONFIG = "Name of the Linux configuration file"
    XEN_SOURCE = "Name of the Xen source file"
    XEN_CONFIG = "Name of the Xen configuration file"
    UBOOT_SOURCE = "Name of the U-Boot source file"
    UBOOT_CONFIG = "Name of the U-Boot configuration file"
    TOOLCHAIN = "specify a toolchain to be used outside of the board execution"
    COLOR = "Turn on or off the console output"
    MI = "Output a JSON machine-interface view of the SBXG library"
    LIB_DIR = """Add a directory to the library search path. When this argument
        is not specified, the lib/ directory of SBXG will be used"""
    BOARD_DIR = """Add a directory to the boards search path. When this argument
        is not specified, the boards/ directory of SBXG will be used"""
    BOARD = "Name of the board configuration file to be processed"


def getopts(argv):
    parser = argparse.ArgumentParser(description='SBXG Boostrapper')
    subparsers = parser.add_subparsers(dest='cmd')

    parser.add_argument("--color", choices=["yes", "no", "auto"],
                        default="auto", help=Help.COLOR)
    parser.add_argument('--lib-dir', '-I', action='append', metavar="LIB_DIR",
                        help=Help.LIB_DIR)
    parser.add_argument('--board-dir', '-B', action='append', metavar="BOARD_DIR",
                        help=Help.BOARD_DIR)

    show = subparsers.add_parser('show')
    show.add_argument("--mi", action='store_true', help=Help.MI)
    show.set_defaults(func=_cmd_show)

    ###########################################################################
    gen = subparsers.add_parser('generate', aliases=['gen'])
    gen.set_defaults(func=_cmd_gen)

    gen.add_argument('--linux-source', '-L', metavar='LINUX_SOURCE',
                     action='append', default=[], help=Help.LINUX_SOURCE)
    gen.add_argument('--linux-config', '-l', metavar='LINUX_CONFIG',
                     action='append', default=[], help=Help.LINUX_CONFIG)
    gen.add_argument('--xen-source', '-X', metavar='XEN_SOURCE',
                     action='append', default=[], help=Help.XEN_SOURCE)
    gen.add_argument('--xen-config', '-x', metavar='XEN_CONFIG',
                     action='append', default=[], help=Help.XEN_CONFIG)
    gen.add_argument('--uboot-source', '-U', metavar='UBOOT_SOURCE',
                     action='append', default=[], help=Help.UBOOT_SOURCE)
    gen.add_argument('--uboot-config', '-u', metavar='UBOOT_CONFIG',
                     action='append', default=[], help=Help.UBOOT_CONFIG)
    gen.add_argument('--toolchain',  '-t', metavar='TOOLCHAIN',
                     default='local', help=Help.TOOLCHAIN)
    gen.add_argument('outdir', metavar='OUTPUT_DIRECTORY', help=Help.OUTDIR)


    ###########################################################################
    board = subparsers.add_parser('board')
    board.set_defaults(func=_cmd_board)
    board.add_argument('board', metavar='BOARD_CONFIG', help=Help.BOARD)

    ###########################################################################
    args = parser.parse_args(argv[1:])

    def _component_args_check(opt_cfg, opt_source):
        # Source Config
        #    0     0      OK
        #    0     1      FAIL
        #    1     0      FAIL
        #    1     1      OK
        src = getattr(args, opt_source.replace('-', '_'))
        cfg = getattr(args, opt_cfg.replace('-', '_'))
        #src = [] if src is None else src
        #cfg = [] if cfg is None else cfg
        if len(src) != len(cfg):
            raise E.SbxgError(f"Options --{opt_cfg} and "
                              f"--{opt_source} must be used together")

    if args.cmd == 'gen':
        for component in ('linux', 'uboot', 'xen'):
            _component_args_check(f"{component}-source", f"{component}-config")

    return args


def main(argv):
    args = getopts(argv)

    # TODO: color==auto
    if args.color == "no":
        for color in ANSI_STYLE:
            ANSI_STYLE[color] = ''

    # The top source directory is where this script resides,
    top_src_dir = Path(__file__).resolve().parent.parent

    # The default lib directory search path is lib/
    if not args.lib_dir:
        args.lib_dir = [top_src_dir / "lib"]
    if not args.board_dir:
        args.board_dir = [top_src_dir / "board"]

    args.func(args, top_src_dir)

if __name__ == "__main__":
    main(sys.argv)

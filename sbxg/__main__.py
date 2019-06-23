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
import shutil
import sys
from pathlib import Path

import sbxg
from sbxg.utils import ANSI_STYLE
from sbxg import error as E

def _cmd_show(args, top_src_dir, top_build_dir):
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


def _cmd_gen(args, top_src_dir, top_build_dir):
    # I forbid you to use the source directory as the build directory!
    if top_src_dir == top_build_dir:
        raise E.SbxgError("Run bootstrap.py from a build directory that is "
                          "distinct from the source directory.")

    # The main database that will hold our configuration
    database = sbxg.model.Database(top_src_dir, top_build_dir)

    toolchain = sbxg.utils.get_toolchain(args.lib_dir, args.toolchain)
    database.set_toolchain(toolchain)

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
    template_dirs = [top_src_dir / "templates"]
    templater = sbxg.template.Templater(database.context(), template_dirs)
    templater.template_file("Makefile.j2", top_build_dir / "Makefile")



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
    MI = "Output a JSON machine-interface view of the SBXG library"
    LIB_DIR = """Add a directory to the library search path. When this argument
        is not specified, the lib/ directory of SBXG will be used"""

def getopts(argv):
    parser = argparse.ArgumentParser(description='SBXG Boostrapper')
    subparsers = parser.add_subparsers(dest='cmd')

    parser.add_argument("--directory", "-C", metavar='DIR', help=Help.CHDIR)
    parser.add_argument("--color", choices=["yes", "no", "auto"],
                        default="auto", help=Help.COLOR)
    parser.add_argument('--lib-dir', '-L', nargs='+', metavar="LIB_DIR",
                        help=Help.LIB_DIR)

    show = subparsers.add_parser('show')
    show.add_argument("--mi", action='store_true', help=Help.MI)
    show.set_defaults(func=_cmd_show)

    ###########################################################################
    gen = subparsers.add_parser('generate', aliases=['gen'])
    gen.set_defaults(func=_cmd_gen)

    gen.add_argument('--kernel-source', '-K', metavar='KERNEL_SOURCE',
                        help=Help.KERNEL_SOURCE)
    gen.add_argument('--kernel-config', '-k', metavar='KERNEL_CONFIG',
                        help=Help.KERNEL_CONFIG)
    gen.add_argument('--xen-source', '-X', metavar='XEN_SOURCE',
                        help=Help.XEN_SOURCE)
    gen.add_argument('--xen-config', '-x', metavar='XEN_CONFIG',
                        help=Help.XEN_CONFIG)
    gen.add_argument('--uboot-source', '-U', metavar='UBOOT_SOURCE',
                        help=Help.UBOOT_SOURCE)
    gen.add_argument('--uboot-config', '-u', metavar='UBOOT_CONFIG',
                        help=Help.UBOOT_CONFIG)
    gen.add_argument('--toolchain',  '-t', metavar='TOOLCHAIN',
                        default='local', help=Help.TOOLCHAIN)
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

    if args.cmd == 'gen':
        for component in ('kernel', 'uboot', 'xen'):
            _component_args_check(f"{component}-source", f"{component}-config")

    return args


def main(argv):
    args = getopts(argv)
    if args.directory:
        os.chdir(args.directory)

    # The top source directory is where this script resides, whereas the build
    # directory is where this script was called from.
    top_src_dir = Path(__file__).resolve().parent.parent
    top_build_dir = Path.cwd().resolve()

    # The default lib directory search path is lib/
    if not args.lib_dir:
        args.lib_dir = [top_src_dir / "lib"]

    args.func(args, top_src_dir, top_build_dir)

if __name__ == "__main__":
    main(sys.argv)

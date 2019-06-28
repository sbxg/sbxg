# Copyright (c) 2019 Jean Guyomarc'h
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
import sys
from pathlib import Path
from pkg_resources import resource_filename

import sbxg
from sbxg.utils import ANSI_STYLE
from sbxg.utils import SbxgError


def _init_top_build_dir(directory):
    # Create the output directory if it does not exist
    Path.mkdir(directory, parents=True, exist_ok=True)
    return directory.resolve()

def _cmd_show(args):
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
        print("\nList of sources:")
        for source in lib["sources"]:
            print(f"  - {stype}{source['type']}{end}:",
                  f"{sname}{source['name']}{end}")
        print("\nList of configurations:")
        for config in lib["configurations"]:
            print(f"  - {stype}{config['type']}{end}:",
                  f"{sname}{config['name']}{end}")
        print("\nList of bootscripts:")
        for bootscript in lib["bootscripts"]:
            print(f" - {sname}{bootscript['name']}{end}")
        print("\nList of images:")
        for image in lib["images"]:
            print(f" - {sname}{image['name']}{end}")
        print("\nList of boards:")
        for board in lib["boards"]:
            print(f" - {sname}{board['name']}{end}")


def _cmd_gen(args):
    top_build_dir = _init_top_build_dir(args.outdir)

    # The main model that will hold our configuration
    model = sbxg.model.Model(top_build_dir)

    toolchain = sbxg.utils.get_toolchain(args.lib_dir, args.toolchain)
    model.set_toolchain(toolchain)

    for src, cfg in zip(args.linux_source, args.linux_config):
        source = sbxg.utils.get_linux_source(args.lib_dir, src)
        config = sbxg.utils.get_linux_config(args.lib_dir, cfg)
        model.add_linux(source, config)

    for src, cfg in zip(args.uboot_source, args.uboot_config):
        source = sbxg.utils.get_uboot_source(args.lib_dir, src)
        config = sbxg.utils.get_uboot_config(args.lib_dir, cfg)
        model.add_uboot(source, config)

    for src, cfg in zip(args.xen_source, args.xen_config):
        source = sbxg.utils.get_xen_source(args.lib_dir, src)
        config = sbxg.utils.get_xen_config(args.lib_dir, cfg)
        model.add_xen(source, config)

    # Now that we are done collecting the data from the configurations, and we
    # have fed our data model, initialize the templating engine.

    template_dirs = [resource_filename('sbxg', 'templates/')]
    templater = sbxg.template.Templater(model.context(), template_dirs)
    templater.template_file("Makefile.j2", top_build_dir / "Makefile")


def _cmd_board(args):
    top_build_dir = _init_top_build_dir(args.outdir)

    # The main model that will hold our configuration
    model = sbxg.model.Model(top_build_dir)

    config = sbxg.utils.get_board_config(args.lib_dir, args.board)
    model.set_board(args.lib_dir, config)

    template_dirs = [resource_filename('sbxg', 'templates/')]
    for lib_dir in args.lib_dir:
        template_dirs.append(lib_dir / "images")
        template_dirs.append(lib_dir / "bootscripts")

    context = model.context()
    board = context["board"]
    templater = sbxg.template.Templater(context, template_dirs)
    templater.template_file("Makefile.j2", top_build_dir / "Makefile")
    templater.template_file(board["boot_script"], top_build_dir / "bootscript.txt")
    templater.template_file(board["disk_image"], top_build_dir / "genimage.cfg")


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
    BOARD = "Name of the board configuration file to be processed"
    NO_BUILTIN = "Do not use SBXG's libraries"


def getopts(argv):
    parser = argparse.ArgumentParser(description='SBXG Boostrapper')
    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True # Set in kwargs in py 3.7

    parser.add_argument("--color", choices=["yes", "no", "auto"],
                        default="auto", help=Help.COLOR)
    parser.add_argument("--no-builtin", action='store_true',
                        help=Help.NO_BUILTIN)
    parser.add_argument('--lib-dir', '-I', action='append', metavar="LIB_DIR",
                        type=Path, help=Help.LIB_DIR, default=[])

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
    gen.add_argument('--toolchain', '-t', metavar='TOOLCHAIN',
                     default='local', help=Help.TOOLCHAIN)
    gen.add_argument('outdir', metavar='OUTPUT_DIRECTORY',
                     type=Path, help=Help.OUTDIR)


    ###########################################################################
    board = subparsers.add_parser('board')
    board.set_defaults(func=_cmd_board)
    board.add_argument('board', metavar='BOARD_CONFIG', help=Help.BOARD)
    board.add_argument('outdir', metavar='OUTPUT_DIRECTORY',
                       type=Path, help=Help.OUTDIR)

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
            raise SbxgError(f"Options --{opt_cfg} and "
                            f"--{opt_source} must be used together")

    if args.cmd == 'gen':
        for component in ('linux', 'uboot', 'xen'):
            _component_args_check(f"{component}-source", f"{component}-config")

    return args


def main(argv=None):
    args = getopts(sys.argv if argv is None else argv)

    # TODO: color==auto
    if args.color == "no":
        for color in ANSI_STYLE:
            ANSI_STYLE[color] = ''

    # By default, add SBXG's own library, unless the user does not want it.
    if not args.no_builtin:
        # The default lib directory search path is lib/
        args.lib_dir.insert(0, Path(resource_filename('sbxg', 'lib/')))

    args.func(args)

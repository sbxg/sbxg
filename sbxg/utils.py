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

import os
import subprocess


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

def get_board_config(search_dirs, board, filename):
    filename = filename + '.yml'
    board_cfg = os.path.join(board, filename)
    for search_dir in search_dirs:
        config_file = os.path.join(search_dir, board_cfg)
        if os.path.isfile(config_file):
            return config_file, os.path.join(search_dir, board)
    raise FileNotFoundError(board_cfg)

def _get_lib_config(lib_dirs, kind, component, filename):
    for lib_dir in lib_dirs:
        config = os.path.join(lib_dir, kind, component, filename)
        if os.path.isfile(config):
            return config
    raise FileNotFoundError(filename)

def get_toolchain(lib_dirs, toolchain):
    return _get_lib_config(lib_dirs, "sources", "toolchain", toolchain + '.yml')

def get_kernel_source(lib_dirs, kernel):
    return _get_lib_config(lib_dirs, "sources", "kernel", kernel + '.yml')

def get_kernel_config(lib_dirs, kernel):
    return _get_lib_config(lib_dirs, "configs", "kernel", kernel)

def get_uboot_source(lib_dirs, uboot):
    return _get_lib_config(lib_dirs, "sources", "uboot", uboot + '.yml')

def get_uboot_config(lib_dirs, uboot):
    return _get_lib_config(lib_dirs, "configs", "uboot", uboot)

def get_xen_source(lib_dirs, xen):
    return _get_lib_config(lib_dirs, "sources", "xen", xen + '.yml')

def get_xen_config(lib_dirs, xen):
    return _get_lib_config(lib_dirs, "configs", "xen", xen)

def get_arch():
    """
    Returns the arch as it is determined by Linux. What is below is the rewritting
    of the SUBARCH variable assignment in Linux' top-level Makefile.
    """
    return subprocess.check_output(
        "uname -m | sed"
        " -e s/i.86/x86/"
        " -e s/x86_64/x86/"
        " -e s/sun4u/sparc64/"
        " -e s/arm.*/arm/"
        " -e s/sa110/arm/"
        " -e s/s390x/s390/"
        " -e s/parisc64/parisc/"
        " -e s/ppc.*/powerpc/"
        " -e s/mips.*/mips/"
        " -e s/sh[234].*/sh/"
        " -e s/aarch64.*/arm64/",
        shell=True,
        universal_newlines=True
    ).rstrip()

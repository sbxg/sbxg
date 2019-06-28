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

from pathlib import Path

class SbxgError(Exception):
    """
    Super class, used by exception handlers to filter-out SBXG-related
    exceptions.
    """

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

def _get_lib_config(lib_dirs, config_file):
    for lib_dir in lib_dirs:
        config = lib_dir / config_file
        if config.is_file():
            return config
    raise SbxgError(f"Failed to find file {config_file} in library")

def get_board_config(lib_dirs, filename):
    return _get_lib_config(lib_dirs, Path("boards", filename + '.yml'))

def get_toolchain(lib_dirs, toolchain):
    return _get_lib_config(lib_dirs, Path("toolchains", toolchain + '.yml'))

def get_linux_source(lib_dirs, linux):
    return _get_lib_config(lib_dirs, Path("sources", "linux", linux + '.yml'))

def get_genimage_source(lib_dirs, genimage):
    return _get_lib_config(lib_dirs, Path("sources", "genimage", genimage + '.yml'))

def get_linux_config(lib_dirs, linux):
    return _get_lib_config(lib_dirs, Path("configs", "linux", linux))

def get_uboot_source(lib_dirs, uboot):
    return _get_lib_config(lib_dirs, Path("sources", "uboot", uboot + '.yml'))

def get_uboot_config(lib_dirs, uboot):
    return _get_lib_config(lib_dirs, Path("configs", "uboot", uboot))

def get_xen_source(lib_dirs, xen):
    return _get_lib_config(lib_dirs, Path("sources", "xen", xen + '.yml'))

def get_xen_config(lib_dirs, xen):
    return _get_lib_config(lib_dirs, Path("configs", "xen", xen))

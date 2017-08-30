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
import pytest
import subprocess
import sys
import tempfile

TOP_SRC_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

@pytest.mark.parametrize("variant", ["xen", "board"])
@pytest.mark.parametrize("toolchain", ["armv7-eabihf"])
def test_cubietruck(variant, toolchain):
    build_dir = tempfile.TemporaryDirectory()

    subprocess.check_call([
        sys.executable,
        os.path.join(TOP_SRC_DIR, "bootstrap.py"),
        "--board", "cubietruck", "--board-variant", variant,
        "--toolchain", toolchain,
    ], cwd=build_dir.name)
    subprocess.check_call([
        "make", "-j2", "-s"
    ], cwd=build_dir.name)


@pytest.mark.parametrize("variant", ["board"])
@pytest.mark.parametrize("toolchain", ["armv7-eabihf"])
def test_orangepi_zero(variant, toolchain):
    build_dir = tempfile.TemporaryDirectory()

    subprocess.check_call([
        sys.executable,
        os.path.join(TOP_SRC_DIR, "bootstrap.py"),
        "--board", "orangepi-zero", "--board-variant", variant,
        "--toolchain", toolchain,
    ], cwd=build_dir.name)
    subprocess.check_call([
        "make", "-j2", "-s"
    ], cwd=build_dir.name)

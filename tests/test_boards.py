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

@pytest.mark.parametrize("variant", ["xen", "board"])
def test_cubietruck(env, variant):
    """Build the cubietruck board with several variants"""
    env.bootstrap_board("cubietruck", "armv7-eabihf", variant)
    env.run_make("-j2")

@pytest.mark.parametrize("variant", ["vexpress-v7"])
def test_virtual(env, variant):
    """Build the virtual board with several variants"""
    env.bootstrap_board("virtual", "armv7-eabihf", variant)
    env.run_make()

@pytest.mark.parametrize("variant", ["board"])
def test_orangepi_zero(env, variant):
    """Build the orange-pi board with several variants"""
    env.bootstrap_board("orangepi-zero", "armv7-eabihf", variant)
    env.run_make("-j2")

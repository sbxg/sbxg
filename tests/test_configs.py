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

TOP_SRC_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

@pytest.mark.parametrize("cfg_type,config", [
    ("toolchain", "toolchains/armv7-eabihf.yml"),
    ("uboot", "uboot/2017.07.yml"),
    ("kernel", "kernels/linux-4.12.0.yml"),
    ("kernel", "kernels/xen-4.8.0.yml"),
    ("board", "boards/cubietruck/board.yml"),
    ("board", "boards/cubietruck/xen.yml"),
])
def test_configs(cfg_type, config):
    """
    This test runs the check-config.py script that resides in the scripts/
    directory, and checks that the configurations distributed by SBXG are
    conformed to the defined schema.
    """
    script = os.path.join(TOP_SRC_DIR, "scripts", "check-config.py")
    config_path = os.path.join(TOP_SRC_DIR, config)
    subprocess.check_call([script, cfg_type, config_path])

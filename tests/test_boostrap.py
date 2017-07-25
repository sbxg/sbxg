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

def test_bootstrap_in_source_dir():
    """
    Running the bootstrap script from the source directory should fail.
    """
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_call([
            sys.executable, "bootstrap.py"
        ], cwd=TOP_SRC_DIR)


@pytest.mark.parametrize("variant", [None, "xen", "board"])
def test_bootstrap_cubietruck(variant):
    cmd = [
        sys.executable,
        os.path.join(TOP_SRC_DIR, "bootstrap.py"),
        "--board", "cubietruck",
        "--no-download",
    ]
    if variant is not None:
        cmd.extend(['--board-variant', variant])

    build_dir = tempfile.TemporaryDirectory()
    subprocess.check_call(cmd, cwd=build_dir.name)

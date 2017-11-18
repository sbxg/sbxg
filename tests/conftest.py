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
import sys
import tempfile

import pytest

TOP_SRC_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class TestEnv(object):
    def __init__(self):
        self._build_dir_handle = tempfile.TemporaryDirectory()
        self.build_dir = self._build_dir_handle.name
        self.rootfs = os.path.join(self.build_dir, "rootfs.ext3")

    def bootstrap_board(self, board, toolchain, variant="board"):
        subprocess.check_call([
            sys.executable,
            os.path.join(TOP_SRC_DIR, "bootstrap.py"),
            "--board", board,
            "--board-variant", variant,
            "--toolchain", toolchain
        ], cwd=self.build_dir)

    def run_make(self, *args):
        """Execute the make command within the build directory, with optional
        arguments to be passed to make
        """
        cmd = ["make"]
        if args:
            cmd.extend(args)
        subprocess.check_call(cmd, cwd=self.build_dir)


@pytest.fixture
def env():
    testenv = TestEnv()

    # Create a dummy ext3 rootfs of 1MB, just for testing purposes
    subprocess.check_call([
        "dd", "if=/dev/zero", "of={}".format(testenv.rootfs),
        "bs=1M", "count=1"])
    subprocess.check_call(["sync"])
    subprocess.check_call(["mkfs.ext3", testenv.rootfs])

    return testenv

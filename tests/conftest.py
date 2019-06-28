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
import subprocess
import sys

import pytest

class TestEnv(object):
    #self.rootfs = os.path.join(self.build_dir, "rootfs.ext3")

    def _run_subprocess(self, cmdline, timeout):
        return subprocess.run(cmdline,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True,
                              timeout=timeout)

    def sbxg(self, args_list):
        cmdline = [sys.executable, "-m", "sbxg"] + args_list
        return self._run_subprocess(cmdline, 60)

    def make(self, directory, target, timeout=60):
        cmdline = ["make", '-C', directory, target]
        return self._run_subprocess(cmdline, timeout)


@pytest.fixture
def env():
    testenv = TestEnv()

    ## Create a dummy ext3 rootfs of 1MB, just for testing purposes
    #subprocess.check_call([
    #    "dd", "if=/dev/zero", "of={}".format(testenv.rootfs),
    #    "bs=1M", "count=1"])
    #subprocess.check_call(["sync"])
    #subprocess.check_call(["mkfs.ext3", "-F", testenv.rootfs])

    return testenv

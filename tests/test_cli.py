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

import json
from pathlib import Path
import tempfile
import pytest

# The three variables below are tuples that are formed as follows:
#  - each entry in the first tuple should be tuple, containing exactly two
#    tuples:
#    - a tuple of SOURCES of a given minor version;
#    - a tuple of CONFIG that are compatible with any SOURCE in the previous
#      tuple.
#
# In the end, it just describes some kind of compatibility matrix between the
# different files, per component, that reside in the builtin SBXG library.
LINUX = (
    [ ["linux-4.12.0"], ["linux-4.12-sunxi"] ],
    [ ["linux-4.14.35"], ["linux-4.14-sunxi-xen-dom0",
                          "linux-4.14-xen-domu"] ],
)
XEN = (
    [ ["xen-4.8.3"], ["xen-4.8-sunxi"] ],
)
UBOOT = (
    [ ["uboot-2017.07"], ["uboot-2017.07-minimal"] ],
)

def _walk_tuples(component):
    for items in component:
        for source in items[0]:
            for config in items[1]:
                yield source, config

@pytest.mark.parametrize("toolchain", [None, "armv7-eabihf"])
def test_gen_builtin_library(env, toolchain):
    """This test tests the 'gen' command by taking parts of the built-in
    library and generating a Makefile able to build all these components.

    We test that the Makefile was properly generated and chekc it has no
    syntax errors (by running 'make help').
    """
    args = ["gen"] # Run the 'gen' command

    for source, config in _walk_tuples(LINUX):
        args.extend(["-L", source, "-l", config])
    for source, config in _walk_tuples(UBOOT):
        args.extend(["-U", source, "-u", config])
    for source, config in _walk_tuples(XEN):
        args.extend(["-X", source, "-x", config])

    if toolchain is not None:
        args.extend(["-t", toolchain])

    # Create a temporary directory, and run the test within.  We just want to
    # generate the Makefile, and check if it does not contains syntactic
    # errors.
    with tempfile.TemporaryDirectory() as tmpdir:
        args.extend(["--", tmpdir])
        # Generate the makefile
        ret = env.sbxg(args)
        assert ret.returncode == 0, f"SBXG failed: {ret.args}"
        # Check that the Makefile was generated
        assert Path(tmpdir, 'Makefile').is_file(), "No Makefile created"
        # Run 'make help', to check there are no syntax error.
        # That's not a very good test, bt I don't feel like downloading and
        # building tenths of Linuxes at every build. At least for now...
        ret = env.make(tmpdir, "help")
        assert ret.returncode == 0, "Makefile seems to be invalid"


def test_show_library(env):
    """This tests the 'show' command. We check that 'sbxg show' does not fail,
    and re-run this test with the machine interface parameter (--mi).  We parse
    the contents of the output returned by --mi and make sure it is meaningful
    with respect to the built-in library
    """
    # First, 'sbxg show' should not fail.
    ret = env.sbxg(["show"])
    assert ret.returncode == 0, "Failed to run a basic show command"

    # Get the contents of 'sbxg show --mi'
    ret = env.sbxg(["show", "--mi"])
    assert ret.returncode == 0, "Failed to run a basic show command"
    data = json.loads(ret.stdout)

    # Check that the returned MI has all the required elements
    mandatory_items = ('sources', 'toolchains', 'configurations', 'boards',
                       'bootscripts', 'images')
    for item in mandatory_items:
        assert item in data, f"MI is missing required field {item}"


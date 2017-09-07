#! /usr/bin/env python3
#
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

import sys
import traceback

import sbxg

def error(message):
    print("{}error:{} {}".format(
        sbxg.utils.ANSI_STYLE['fail'],
        sbxg.utils.ANSI_STYLE['endc'],
        message,
    ), file=sys.stderr)


# Run the main entry point. We will also catch all the exceptions to
# pretty-format the reason of failure.
if __name__ == "__main__":
    try:
        sbxg.runner.main(sys.argv)
    except sbxg.error.SbxgError as exception:
        # SBXG will raise its own errors through custom exceptions. They are
        # already well-formated, and correspond to nominal failures.
        error(exception)
        sys.exit(1)
    except Exception:
        # Generale exceptions are the one not planned by SBXG.
        error("Unhandled error! Please report the following trace:")
        traceback.print_exc(file=sys.stderr)
        error("Aborting!")
        sys.exit(127)

#! /usr/bin/env python
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

import argparse
import subprocess
import sys

def getopts(argv):
    parser = argparse.ArgumentParser(description='Rootfs generator')
    parser.add_argument(
        '--mkfs', type=str, default='ext3',
        help='Type of filesystem to be generated. This option is passed to mkfs'
    )
    parser.add_argument(
        '--ok', action='store_true',
       help='Use this option to confirm the commands to be run'
    )
    parser.add_argument(
        'rootfs_dir', type=str,
        help='Path to the directory containing the rootfs'
    )
    parser.add_argument(
        'output', type=str,
        help='Path to the filesystem block to be created'
    )
    parser.add_argument(
        'size', type=int,
        help='Size (in MB) of the output filesystem'
    )
    return parser.parse_args(argv[1:])

def main(argv):
    args = getopts(argv)

    cmds = []
    cmds.append("dd if=/dev/zero of={} bs=1M count={} iflag=fullblock".format(
        args.output, args.size
    ))
    cmds.append("sync")
    cmds.append("mkfs.{} -d {} {}".format(
        args.mkfs, args.rootfs_dir, args.output
    ))


    if args.ok:
        for cmd in cmds:
            print("Running {}".format(cmd))
            subprocess.check_call(cmd.split(' '))
    else:
        print("The following commands are planned to be run:\n")
        for cmd in cmds:
            print("  {}".format(cmd))
        print("\nRe-run with the --ok option to run them.")

if __name__ == "__main__":
    main(sys.argv)

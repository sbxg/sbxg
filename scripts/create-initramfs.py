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
import os
import subprocess
import sys

FSTAB = """# SBXG-Powered fstab for busybox
# <file system> <mount point>   <type>  <options>       <dump>  <pass>
proc            /proc           proc    defaults        0       0
sysfs           /sys            sysfs   defaults        0       0
"""

RCS = """# SBXG-Powered rcS for busybox
#! /bin/sh

set +e # Do *NOT* fail on error!!!
/bin/mount -a # Mount things in fstab.
/bin/mount -t devtmpfs devtmpfs /dev # Mount devtmpfs
cat /etc/motd # Say welcome
"""

MOTD = """
        ____  ____  _  _  ___
       / ___)(  _ \( \/ )/ __)
       \___ \ ) _ ( )  (( (_ \\
       (____/(____/(_/\_)\___/


"""

def getopts(argv):
    parser = argparse.ArgumentParser(description='Initramfs packager')
    parser.add_argument(
        'path', type=str,
        help='Path to the busybox build directory'
    )
    parser.add_argument(
        '--output', '-o', type=str, default='initramfs.cpio',
        help='Path where the initramfs will be generated'
    )
    return parser.parse_args(argv[1:])


def main(argv):
    args = getopts(argv)

    # This part shall be executed in the busysbox install dir
    cwd = os.getcwd()
    os.chdir(args.path)

    # Create some mountpoints and the configuration directory
    for new_dir in ["dev", "proc", "sys", "mnt", "etc/init.d"]:
        os.makedirs(new_dir, exist_ok=True)

    # Symlink /init to /sbin/init
    if not os.path.exists("init"):
        os.symlink("/sbin/init", "init")

    # Create the fstab, initial configuration and motd
    with open('etc/fstab', 'w') as stream:
        stream.write(FSTAB)
    with open('etc/init.d/rcS', 'w') as stream:
        stream.write(RCS)
    with open('etc/motd', 'w') as stream:
        stream.write(MOTD)

    # Make the initial configuration executable
    os.chmod('etc/init.d/rcS', 0o755)

    # Run cpio to create the initramfs
    output = subprocess.check_output(
        "find . -print | cpio --quiet -o --format=newc", shell=True
    )

    # Change directory back, so we don't have to recalculate thhe output path
    os.chdir(cwd)
    # Write the initramfs on the filesystem
    with open(args.output, 'wb') as stream:
        stream.write(output)

if __name__ == "__main__":
    main(sys.argv)

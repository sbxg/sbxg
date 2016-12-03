#! /usr/bin/env sh
#
# Copyright (c) 2016, Jean Guyomarc'h <jean@guyomarch.bzh>
#
# This file is part of SBXG
#
# SBXG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SBXG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SBXG.  If not, see <http://www.gnu.org/licenses/>.

set -e
set -u

# Getopt
if [ $# -ne 2 ]; then
   echo "*** Usage: $0 BUSYBOX_BUILD_DIR INITRAMFS" 1>&2
   exit 1
fi
BUSYBOX_BUILD_DIR="$1"
INITRAMFS="$(realpath "$2")"

# Get where busybox installed itself
cd "$BUSYBOX_BUILD_DIR"
DIR="$(grep "^CONFIG_PREFIX=" .config | cut -d '=' -f 2 | sed 's/"//g')"

# Go into busybox directoy
cd "$DIR"

# Create directories that will be included to the initramfs
mkdir -p dev
mkdir -p proc
mkdir -p sys
mkdir -p mnt
mkdir -p etc/init.d

# /init may be required. Alias it to /sbin/init
ln -sf /sbin/init init

# Create an fstab to auto-mount proc and sysfs
cat <<EOF > etc/fstab
# <file system> <mount point>   <type>  <options>       <dump>  <pass>
proc            /proc           proc    defaults        0       0
sysfs           /sys            sysfs   defaults        0       0
EOF

# Create an init script to boot on a nice initramfs
cat <<EOF > etc/init.d/rcS
#! /bin/sh

# Do NOT fail on error!!!
set +e

# Mount things in fstab.
/bin/mount -a

# Mount devtmpfs in /dev
mkdir -p /dev
/bin/mount -t devtmpfs devtmpfs /dev

# Say welcome
cat /etc/motd
EOF
chmod +x etc/init.d/rcS

# Create a welcome message
cat <<EOF > etc/motd
           _  _
          | ||_|
          | | _ ____  _   _  _  _
          | || |  _ \\| | | |\\ \\/ /
          | || | | | | |_| |/    \\
          |_||_|_| |_|\\____|\\_/\\_/

            Busybox Rootfs (SBXG)
EOF

# Create the initramfs
find . -print | cpio -o --format=newc > "$INITRAMFS"

#! /usr/bin/env bash
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

set -e
set -u

HERE=$(dirname "$0")
XEN_SUPPORT=no
OUTPUT_FILE="rootfs.ext3"
ROOTFS_SIZE=512
HOOK=

while getopts "xo:s:h:" opt; do
   case $opt in
      x)
         XEN_SUPPORT=yes
         ;;
      o)
         OUTPUT_FILE="$OPTARG"
         ;;
      s)
         ROOTFS_SIZE="$OPTARG"
         ;;
      h)
         HOOK="$OPTARG"
         ;;
   esac
done

# Remove the extension from the output file, so we can deduce a directory that
# will be used to debootstrap into
output_dir="${OUTPUT_FILE%.*}"
if [ "x$output_dir" = "x$OUTPUT_FILE" ]; then
   echo "*** The argument passed to -o shall have an extension (e.g. .ext3)" 1>&2
   exit 1
fi

set -x

# Debootstrap: we do a two-stages foreign debootstrap, with qemu-arm-static to
# post-configure the debootstrap
debootstrap --foreign --arch armhf stable "$output_dir" http://ftp.debian.org/debian
cp $(which qemu-arm-static) "$output_dir/usr/bin"
chroot "$output_dir" /debootstrap/debootstrap --second-stage
chroot "$output_dir" dpkg --configure -a

# "root" will have a password "root", so we can easily log in the first time!
echo "root:root" | chroot "$output_dir" chpasswd

# If the rootfs requires Xen, install the xen tools.
if [ "x$XEN_SUPPORT" = "xyes" ]; then
   chroot "$output_dir" apt install -y --allow-unauthenticated xen-tools
fi

# Execute a custom configuration hook
if test -n "$HOOK"; then
   "$HOOK" "$output_dir"
fi

# Remove the native qemu-arm-static to leave a clean rootfs
rm "$output_dir/usr/bin/qemu-arm-static"

# Now, create an ext3 filesystem with the debootstrap
"$HERE/gen-rootfs.py" --ok "$output_dir" "$OUTPUT_FILE" "$ROOTFS_SIZE"

#! /usr/bin/env sh
#
#
# Copyright (c) 2015-2016, Jean Guyomarc'h <jean.guyomarch@gmail.com>
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
set -x

# Source the main configuration
. "$(dirname "$0")"/config

# Debian packages to generate with make-kpkg
DEB_PACKAGES="
kernel_image
kernel_headers
kernel_doc
kernel_source
"

# Where debian files will be placed and patched
DEB_DIR_OVERLAY="$PWD/debian_overlay"


#==============================================================================#
#                          Create the debian packages                          #
#==============================================================================#

# SHA1 of build tool
SHA1_BASE=$(git rev-parse --short HEAD)

cd "$CONFIG_LINUX_DIR"

# Generate kernel.release if missing
make ARCH=arm include/config/kernel.release

# SHA1 of Linux Kernel
SHA1_KERNEL=$(git rev-parse --short HEAD)
KERNEL_VERSION="$(cat "include/config/kernel.release" | cut -f 1 -d '-')"

DISABLE_PAX_PLUGINS=y \
LOADADDR="$CONFIG_LOADADDR" \
DEB_HOST_ARCH="$CONFIG_ARCH" \
make-kpkg --rootcmd fakeroot \
          --revision "${KERNEL_VERSION}+${SHA1_BASE}~${SHA1_KERNEL}" \
          --uimage \
          --append_to_version "-${SHA1_BASE}-${SHA1_KERNEL}" \
          --jobs "$CONFIG_JOBS" \
          --initrd \
          --arch arm \
          --cross-compile "$CONFIG_GCC_PREFIX" \
          $DEB_PACKAGES

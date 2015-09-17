#!/bin/sh

set -ex

# Source the configuration
. ./config.user

# Debian packages to generate with make-kpkg
DEB_PACKAGES=

# Where debian files will be placed and patched
DEB_DIR_OVERLAY="$PWD/debian_overlay"



# Prints in stderr
# @param $@ arguments printed to stderr
err() {
   echo "*** $@" 1>&2
}

# Give info about how to use this script
usage() {
   echo "Usage: $0 { kernel_image, kernel_headers, kernel_doc, kernel_source }"
}


# =========================================================================== #
# Tiny getopt
#  - checks that all arguments are valid
#  - checks that at least one package can be generated
# =========================================================================== #
for arg in $@; do
   case "$arg" in
      kernel_image)
         DEB_PACKAGES="$DEB_PACKAGES $arg"
         ;;

      kernel_headers)
         DEB_PACKAGES="$DEB_PACKAGES $arg"
         ;;

      kernel_doc)
         DEB_PACKAGES="$DEB_PACKAGES $arg"
         ;;

      kernel_source)
         DEB_PACKAGES="$DEB_PACKAGES $arg"
         ;;

      *)
         err "Invalid input parameter $arg"
         usage 1>&2
         exit 1
         ;;
   esac
done
if [ -z "$DEB_PACKAGES" ]; then
   err "No debian package specified"
   usage 1>&2
   exit 1
fi

#==============================================================================#
#                          Create the debian packages                          #
#==============================================================================#

# SHA1 of build tool
SHA1_BASE=$(git rev-parse --short HEAD)

cd "$LINUX_DIR"

# Generate kernel.release if missing
make ARCH=arm include/config/kernel.release

# SHA1 of Linux Kernel
SHA1_KERNEL=$(git rev-parse --short HEAD)
KERNEL_VERSION="$(cat "include/config/kernel.release" | cut -f 1 -d '-')"

DISABLE_PAX_PLUGINS=y \
LOADADDR="$LOADADDR" \
DEB_HOST_ARCH="$DEB_ARCH" \
make-kpkg --rootcmd fakeroot \
          --revision "${KERNEL_VERSION}+${SHA1_BASE}~${SHA1_KERNEL}" \
          --uimage \
          --append_to_version "-${SHA1_BASE}-${SHA1_KERNEL}" \
          --jobs "$JOBS" \
          --initrd \
          --arch arm \
          --cross-compile "$GCC_PREFIX" \
          $DEB_PACKAGES


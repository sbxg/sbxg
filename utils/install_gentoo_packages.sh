#! /usr/bin/env sh

set -e
set -u

THIS_DIR="$(dirname "$0")"

set -x

# Installing the Ebuilds
sudo emerge --ask \
    dev-vcs/git \
    sys-devel/autoconf \
    sys-devel/automake \
    dev-libs/confuse


# Installing the python packages
pip3 install --user -r "$THIS_DIR/requirements.txt"

# Installing rust (not packaged)
curl https://sh.rustup.rs -sSf | sh

# Cargo setup
"$THIS_DIR"/cargo_setup.sh

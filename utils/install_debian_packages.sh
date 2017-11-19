#! /usr/bin/env sh

set -e
set -u

THIS_DIR="$(dirname "$0")"

set -x

# Installing the Debian packages
sudo apt install \
   build-essential \
   git \
   make \
   curl \
   autoconf \
   autotools-dev \
   swig \
   python-dev \
   libconfuse-dev \
   mtools \
   python3-pip

# Installing the python packages
pip3 install --user -r "$THIS_DIR/requirements.txt"

# Installing rust (not packaged)
curl https://sh.rustup.rs -sSf | sh

# Cargo setup
"$THIS_DIR"/cargo_setup.sh

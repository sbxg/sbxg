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


# Installing the python packages
pip3 install --user -r "$THIS_DIR/requirements.txt"

# Installing rust (not packaged)
curl https://sh.rustup.rs -sSf | sh

# Installing subcomponent
cargo install subcomponent

set +x
echo
echo "=========================================================================="
echo
echo " To complete your setup, please add the following line to your ~/.profile"
echo " file or equivalent:"
echo
echo '    export PATH="$PATH:$HOME/.cargo/bin"'
echo
echo
echo " You will also need to execute this line in your shell to be able to run"
echo " SBXG from this shell."
echo "=========================================================================="

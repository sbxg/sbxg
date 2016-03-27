#! /usr/bin/env sh

# Copyright (c) 2013-2014, Sylvain Leroy <sylvain@unmondelibre.fr>
#                    2014, Jean-Marc Lacroix <jeanmarc.lacroix@free.fr>
#                    2014, Philippe Thierry <phil@reseau-libre.net>
#                    2015, Jean Guyomarc'h <jean.guyomarch@gmail.com>
#                    2015, Louis Syoën <louis.syoen@openmailbox.org>

# This file is part of SBXG.

# SBXG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# SBXG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with SBXG.  If not, see <http://www.gnu.org/licenses/>.

set -x
set -e

#############
# VARIABLES #
#############

# Source the main configuration
. "$(dirname "$0")"/config

set -u

# On some systems (e.g. Arch Linux), PATH is unset
CHROOT_PATH="/bin:/usr/bin:/sbin:/usr/sbin"

############
# FUNCTION #
############

do_debootstrap()
{
    set -x

    # Check for debootstrap binary
    if [ ! -x "$CONFIG_DEBOOTSTRAP" ]; then
       echo "WARNING: $CONFIG_DEBOOTSTRAP is not explicitely defined"
       CONFIG_DEBOOTSTRAP="debootstrap"
    fi

    sudo http_proxy="$CONFIG_DEBOOTSTRAP_HTTP_PROXY" \
       "$CONFIG_DEBOOTSTRAP" \
       --foreign \
       --arch "$CONFIG_ARCH" \
       "$CONFIG_DEBOOTSTRAP_DISTRIBUTION" \
       "$CONFIG_CHROOT_DIR" \
       "$CONFIG_DEBOOTSTRAP_MIRROR"

# that command is useful to run target host binaries (ARM) on the build host (x86)
    qemu_path="$(which "$CONFIG_QEMU_ARM_STATIC")"
    sudo cp "$qemu_path" "$CONFIG_CHROOT_DIR"/usr/bin

# if you use grsecurity on build host, you should uncomment that line
#sudo /sbin/paxctl -cm usr/bin/qemu-arm-static
#sudo /sbin/paxctl -cpexrms usr/bin/qemu-arm-static

# debootstrap second stage and packages configuration
    sudo LC_ALL=C LANGUAGE=C LANG=C chroot "$CONFIG_CHROOT_DIR" /debootstrap/debootstrap --second-stage
    sudo LC_ALL=C LANGUAGE=C LANG=C PATH="$CHROOT_PATH" chroot "$CONFIG_CHROOT_DIR" dpkg --configure -a

    set +x
}

##########

configure_system()
{
# set root password

    if [ -z "$CONFIG_ROOT_PASSWORD" ]; then
        echo "Please enter the root password: "
        # hiding the root password when typed could be a good idea... (stty)
	read -r CONFIG_ROOT_PASSWORD
    fi
    sudo PATH="$CHROOT_PATH" bash -c "echo -e root:$CONFIG_ROOT_PASSWORD | chroot $CONFIG_CHROOT_DIR chpasswd"

# set admin account

    if [ -z "$CONFIG_ADMIN_PASSWORD" ]; then
    # hiding the root password when typed could be a good idea... (stty)
        echo "Please enter the admin password: "
	read -r CONFIG_ADMIN_PASSWORD
    fi

    # Evaluate whether we should create admin and add it to sudoers
    CREATE_USER=1
    ADD_TO_SUDOER=1

    # FIXME This is pointless! We are doing this test in the host, not in the chroot...
    #set +e
    #getent passwd admin
    #if [ $? -eq 0 ]; then
    #   CREATE_USER=0
    #   groups admin | grep sudo &> /dev/null
    #   if [ $? -eq 0 ]; then
    #      ADD_TO_SUDOER=0
    #   fi
    #fi

    if [ "$CREATE_USER" -eq 1 ]; then
       sudo PATH="$CHROOT_PATH" bash -c "chroot $CONFIG_CHROOT_DIR useradd admin"
    fi
    if [ "$ADD_TO_SUDOER" -eq 1 ]; then
       sudo PATH="$CHROOT_PATH" bash -c "chroot $CONFIG_CHROOT_DIR adduser admin sudo"
    fi
    sudo PATH="$CHROOT_PATH" bash -c "echo -e admin:$CONFIG_ADMIN_PASSWORD | chroot $CONFIG_CHROOT_DIR chpasswd"
    set -e

# this set -x does not appear before previous sudo, not to show the root password on the output.
    set -x

# set hostname

    if [ -z "$CONFIG_HOSTNAME" ]; then
        echo "Please enter the hostname of the host: "
        read -r CONFIG_HOSTNAME
    fi
    sudo PATH="$CHROOT_PATH" bash -c "echo $CONFIG_HOSTNAME > $CONFIG_CHROOT_DIR/etc/hostname"

# check if a serial console already exist in the inittab file
# we remove the error check to let grep output an error if the file does not have the line we look for
    if  [ -f "$CONFIG_CHROOT_DIR"/etc/inittab ]; then
      set +e
      grep 'T0:2345:respawn:/sbin/getty -L ttyS0 115200 vt100' "$CONFIG_CHROOT_DIR"/etc/inittab
      RET_VALUE=$?
      set -e

      if [ 0 -ne "$RET_VALUE" ]; then
         # add serial console to connect to the system
         sudo bash -c "echo \"T0:2345:respawn:/sbin/getty -L ttyS0 115200 vt100\" >> $CONFIG_CHROOT_DIR/etc/inittab"
      fi
    fi

# disable some local consoles
# sed -i 's/^\([3-6]:.* tty[3-6]\)/#\1/' /etc/inittab

# copy basic templates of configuration files
    sudo cp "$CONFIG_RESOURCES_DIR/fstab.base" "$CONFIG_CHROOT_DIR"/etc/fstab
    sudo cp "$CONFIG_RESOURCES_DIR/interfaces.base" "$CONFIG_CHROOT_DIR"/etc/network/interfaces

    set +x
}

##########

update_system_and_custom_packages()
{
    set -x
    apt_proxy="etc/apt/apt.conf.d/99proxy"

# tmp stuff
    if  [ -e "/etc/resolv.conf" ]; then
       sudo cp /etc/resolv.conf "$CONFIG_CHROOT_DIR"/etc
    fi

# updating root_fs
    sudo bash -c "echo deb http://http.debian.net/debian/ $CONFIG_DEBOOTSTRAP_DISTRIBUTION main contrib non-free > $CONFIG_CHROOT_DIR/etc/apt/sources.list"
    sudo bash -c "echo deb http://security.debian.org/ $CONFIG_DEBOOTSTRAP_DISTRIBUTION/updates main contrib non-free >> $CONFIG_CHROOT_DIR/etc/apt/sources.list"
    sudo mkdir -p "$CONFIG_CHROOT_DIR"/etc/apt/apt.conf.d
    if [ -f "/$apt_proxy" ]; then
        sudo bash -c "cp /$apt_proxy $CONFIG_CHROOT_DIR/$apt_proxy"
    fi
    sudo PATH="$CHROOT_PATH" chroot "$CONFIG_CHROOT_DIR" apt-get update

    # Install brcmfmac firmware for Cubietruck (wifi/BT)
    if [ x"$CONFIG_BOARD" = "xCubietruck" ]; then
        sudo PATH="$CHROOT_PATH" chroot "$CONFIG_CHROOT_DIR" apt-get install --yes firmware-brcm80211
        if [ ! -d "$CONFIG_CHROOT_DIR"/lib/firmware/brcm ]; then
            echo "*** Failed to install firmware" 1>&2
            exit 1
        else
            sudo cp "$CONFIG_RESOURCES_DIR/brcmfmac43362-sdio.txt" "$CONFIG_CHROOT_DIR"/lib/firmware/brcm/
        fi
    fi

# install additionnals packages
### Here $PACKAGES MUST be without double quotes or apt-get won't understand the list of packages
    sudo PATH="$CHROOT_PATH" chroot "$CONFIG_CHROOT_DIR" apt-get install --yes $CONFIG_PACKAGES

# removing tmp stuff
    sudo PATH="$CHROOT_PATH" chroot "$CONFIG_CHROOT_DIR" apt-get clean
    sudo PATH="$CHROOT_PATH" chroot "$CONFIG_CHROOT_DIR" apt-get autoclean
    sudo rm -f "$CONFIG_CHROOT_DIR"/etc/resolv.conf
    sudo rm -f "$CONFIG_CHROOT_DIR"/"$apt_proxy"

    set +x
}

##########

install_kernel()
{
    set -x

    # Install kernel (uImage, DTB, modules)
    sudo cp "$CONFIG_LINUX_DIR/.config" "$CONFIG_CHROOT_DIR"/boot/config
    sudo cp "$CONFIG_LINUX_DIR/arch/arm/boot/dts/$CONFIG_DTB" "$CONFIG_CHROOT_DIR"/boot
    sudo cp "$CONFIG_LINUX_DIR/arch/arm/boot/uImage" "$CONFIG_CHROOT_DIR"/boot
    sudo make -C "$CONFIG_LINUX_DIR" INSTALL_MOD_PATH="$(realpath "$CONFIG_CHROOT_DIR")" ARCH=arm modules_install

# add some kernel boot args
    mkimage -C none -A arm -T script -d boot.cmd boot.scr
    sudo mv boot.scr "$CONFIG_CHROOT_DIR"/boot/
    sudo chown root:root "$CONFIG_CHROOT_DIR"/boot/boot.scr
    set +x
}


hook_image_postinstall()
{
   set -x

   # Execute image-postinstall hook
   if [ -d "$CONFIG_HOOKS_DIR" ]; then
      if [ -x "$CONFIG_HOOKS_DIR/image-postinstall" ]; then
         "$CONFIG_HOOKS_DIR"/image-postinstall "$CONFIG_CHROOT_DIR"
      fi
   fi

   set +x
}

##########

########
# MAIN #
########

# create the chroot if it doesn't exist
mkdir -p "$CONFIG_CHROOT_DIR"

case "$1" in
    all)
	do_debootstrap
	configure_system
	update_system_and_custom_packages
	install_kernel
	;;
    debootstrap)
	do_debootstrap
	;;
    config)
	configure_system
	;;
    custom)
	update_system_and_custom_packages
	;;
    kernel)
	install_kernel
	;;
    image_postinstall)
        hook_image_postinstall
        ;;
    *)
	echo "Usage: make_debootstrap.sh {all|debootstrap|config|custom|kernel|image_postinstall}"
	exit 1
esac

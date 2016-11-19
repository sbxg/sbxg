# -*- mode: ruby -*-
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

Vagrant.configure(2) do |config|
  config.vm.box = "debian/jessie64"

  config.vm.synced_folder ".", "/srv/sbxg"

  config.vm.provider "virtualbox" do |vb|
    vb.gui = false
    vb.memory = "256"
  end

  config.vm.provision "shell", inline: <<-SHELL
    sudo apt-get update
    sudo apt-get install -y curl

    # Install emdebian toolchain
    sudo bash -c "echo 'deb http://emdebian.org/tools/debian/ jessie main' >> /etc/apt/sources.list"
    curl http://emdebian.org/tools/debian/emdebian-toolchain-archive.key | sudo apt-key add -
    sudo dpkg --add-architecture armhf
    sudo apt-get update

    # Install REPO
    sudo curl https://storage.googleapis.com/git-repo-downloads/repo -o /usr/bin/repo
    sudo chmod +x /usr/bin/repo

    # Packages required
    sudo apt-get install -y apt-utils
    sudo apt-get install -y autoconf
    sudo apt-get install -y build-essential
    sudo apt-get install -y make
    sudo apt-get install -y automake
    sudo apt-get install -y qemu-user-static
    sudo apt-get install -y qemu
    sudo apt-get install -y cmake
    sudo apt-get install -y binfmt-support
    sudo apt-get install -y git
    sudo apt-get install -y kernel-package
    sudo apt-get install -y u-boot-tools
    sudo apt-get install -y sudo
    sudo apt-get install -y debootstrap
    sudo apt-get install -y parted
    sudo apt-get install -y kpartx
    sudo apt-get install -y libncurses5-dev
    sudo apt-get install -y python3
    sudo apt-get install -y crossbuild-essential-armhf

    sudo apt-get clean

    # Configure git - needed for repo
    git config --global user.email "vagrant@vm"
    git config --global user.name "Vagrant"
  SHELL
end

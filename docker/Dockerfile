# Copyright (c) 2015-2016, Jean Guyomarc'h <jean@guyomarch.bzh>
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


FROM debian:8.2
MAINTAINER Jean Guyomarc'h <jean@guyomarch.bzh>

RUN apt-get update
RUN apt-get install -y curl

RUN echo "deb http://emdebian.org/tools/debian/ jessie main" >> /etc/apt/sources.list
RUN curl http://emdebian.org/tools/debian/emdebian-toolchain-archive.key -o key
RUN apt-key add key
RUN dpkg --add-architecture armhf

# Install repo
RUN curl https://storage.googleapis.com/git-repo-downloads/repo > /usr/bin/repo
RUN chmod +x /usr/bin/repo

RUN apt-get update

RUN apt-get install -y apt-utils
RUN apt-get install -y crossbuild-essential-armhf
RUN apt-get install -y autoconf
RUN apt-get install -y build-essential
RUN apt-get install -y make
RUN apt-get install -y automake
RUN apt-get install -y qemu-user-static
RUN apt-get install -y qemu
RUN apt-get install -y cmake
RUN apt-get install -y binfmt-support
RUN apt-get install -y git
RUN apt-get install -y kernel-package
RUN apt-get install -y u-boot-tools
RUN apt-get install -y sudo
RUN apt-get install -y debootstrap
RUN apt-get install -y parted
RUN apt-get install -y kpartx
RUN apt-get install -y libncurses5-dev
RUN apt-get install -y python3.4

RUN apt-get clean

RUN mkdir -p /opt/sbxg
VOLUME /opt/sbxg

USER root
WORKDIR /opt/sbxg

RUN git config --global user.email "docker@container"
RUN git config --global user.name "Docker"

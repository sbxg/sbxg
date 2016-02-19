# Copyright (c) 2013-2014, Sylvain Leroy <sylvain@unmondelibre.fr>
#                    2014, Jean-Marc Lacroix <jeanmarc.lacroix@free.fr>
#               2015-2016, Jean Guyomarc'h <jean.guyomarch@gmail.com>
#                    2015, Damien Pradier <damien.pradier@epita.fr>
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

SED := sed
SCRIPTS_DIR := scripts
MAKE_DIR := make
DEPS := makefile.vars Makefile

MANIFESTS_URL := $(shell $(SCRIPTS_DIR)/get_remote_url.sh)/manifests
MANIFEST ?= linux


export

# makefile.vars is automatically generated by this Makefile. Therefore it
# does not exist at the first execution of make. The "-" before include
# means "don't complain if the file is non-existant".
# When a target needs makefile.vars, this Makefile launches the script
# that generated makefile.vars. At the end of this target, make restarts
# itself and tries again to include makefile.vars. But this time, it exists
# therefore everything can work as expected :)
-include makefile.vars


all: $(DEPS) u-boot linux-defconfig linux debootstrap prepare_sdcard
	@echo "Done. You can now use your $(BOARD_NAME) :)"

include $(MAKE_DIR)/common.mk
include $(MAKE_DIR)/linux.mk
include $(MAKE_DIR)/u-boot.mk

.PHONY: help all \
   debootstrap prepare_sdcard \
   clean distclean debian \
   init sync repo-clean

help: $(DEPS)
	@echo "What you can do:"
	@echo
	@echo "init:                    Usage: make BOARD=<> init. Inits SBNG for a given board"
	@echo "all:			Will do all the job for you."
	@echo
	@echo "config:                  Generate a user config from the template"
	@echo
	@echo "  -- kernel configuration --"
	@echo "linux-<TARGET>		Will call <TARGET> in the linux directory. E.g linux-menuconfig"
	@echo
	@echo "  -- kernel compilation --"
	@echo "linux:			make ARCH=arm CROSS_COMPILE=$(GCC_PREFIX) uImage modules"
	@echo
	@echo "  -- make-kpkg --"
	@echo "debian			generated debian packages of the kernel with make-kpkg"
	@echo
	@echo "  -- u-boot compilation --"
	@echo "u-boot:			make CROSS_COMPILE=$(GCC_PREFIX) $(BOARD_NAME)_config"
	@echo
	@echo "  -- root_fs & sdcard partitionning --"
	@echo "debootstrap:		create the root_fs (need testing)"
	@echo "prepare_sdcard:		install u-boot and the root_fs to the sdcard"
	@echo
	@echo "  -- cleaning targets --"
	@echo "clean:			clean the compiled files (not done yet)"
	@echo "distclean:		clean the compilet files and the root_fs"
	@echo "repo-clean:              clears repo internal state"
	@echo
	@echo "  -- Environnement variables --"
	@echo "	LINUX_DIR		=	$(LINUX_DIR)"
	@echo "	UBOOT_DIR		=	$(UBOOT_DIR)"
	@echo "	CHROOT_DIR		=	$(CHROOT_DIR)"
	@echo "	GCC_PREFIX		=	$(GCC_PREFIX)"
	@echo "	JOBS			=	$(JOBS)"
	@echo "	HOSTNAME		=	$(HOSTNAME)"
	@echo "	PACKAGES		=	$(PACKAGES)"
	@echo "	BOARD_NAME		=	$(BOARD_NAME)"
	@echo
	@echo "	You can and MUST configure these variables from the file : makefile.vars"
	@echo


config.user: config.template
	cp $< $@

makefile.vars: config.user
	$(SCRIPTS_DIR)/genvars.sh

config: config.user


debian: $(DEPS)
	$(SCRIPTS_DIR)/make_debian_packages.sh $(LINUX_DEBIAN_PACKAGES)

boot.cmd: $(DEPS) boot.cmd.in
	$(SED) \
	   -e 's|@DTB@|$(DTB)|g' \
	   -e 's|@ROOTFS@|$(ROOTFS)|g' \
	   boot.cmd.in > $@

debootstrap: $(DEPS) boot.cmd
	$(SCRIPTS_DIR)/make_debootstrap.sh all

prepare_sdcard: $(DEPS)
	$(SCRIPTS_DIR)/prepare_sdcard.sh all

# Cleaning stuff

clean: $(DEPS) u-boot-clean linux-clean
	$(RM) makefile.vars
	$(RM) config.user
	$(RM) boot.cmd
	$(RM) .board


distclean: $(DEPS) clean u-boot-distclean linux-distclean
	sudo $(RM) -r $(CHROOT_DIR)

mrproper: $(DEPS) distclean u-boot-mrproper linux-mrproper repo-clean

init:
ifeq ($(BOARD),)
	@echo "*** You need to provide the board via 'make BOARD=xxx init'"
else
# Keep track of the board name, to be able to source the config later
	echo "$(BOARD)" > .board
	repo init -u $(MANIFESTS_URL) -m "$(BOARD)/$(MANIFEST).xml"
	$(MAKE) sync
endif

sync:
	repo sync
	$(SCRIPTS_DIR)/genvars.sh

repo-clean:
	$(RM) .board
	$(RM) -r .repo

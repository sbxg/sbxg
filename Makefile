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


# Since there are several include files, 'all' is not going to be the
# first target, and therefore not the default target.
# Let's ensure the default goal is 'all'.
.DEFAULT_GOAL := all

# Configuration parameters
include makefile.vars

# Determine whether config exists or not
ifneq ($(findstring .config,$(wildcard ./$(CONFIG))),)
   HAS_CONFIG = y
   include $(CONFIG)
else
   HAS_CONFIG = n
endif


   # It gets a bit tricky here. .config stores strings with double quotes.
   # That's Okay: it's understood by shells when composing arguments,
   # because they are implicitely cut. Make, however, does not!
   # This expansion will allow the Shell to provide a valid string
   # for Make.
   BOARD_CONFIG := $(shell echo "$(BOARDS_DIR)/$(CONFIG_BOARD).conf")
   ifneq ($(findstring $(BOARD_CONFIG),$(wildcard ./$(BOARD_CONFIG))),)
      HAS_BOARD_CONFIG = y
   else
      HAS_BOARD_CONFIG = n
   endif

-include $(BOARD_CONFIG)
# Include other components of the build system
include $(MAKE_DIR)/common.mk
include $(MAKE_DIR)/menuconfig.mk
include $(MAKE_DIR)/linux.mk
include $(MAKE_DIR)/u-boot.mk

ifeq ($(CONFIG_DEBUG_SBXG),y)
   export MAKE_SHELL := $(SHELL)
   SHELL := $(SCRIPTS_DIR)/hooker.sh
endif

MAKEFILE_DEPS := makefile.vars Makefile

# $(DEPS) allow to rebuild targets when main configuration files or
# the build system have been alterated.
DEPS := $(MAKEFILE_DEPS) $(CONFIG)


.PHONY: all

ALL_TARGETS := board-config-required $(DEPS) u-boot linux-defconfig linux
ifeq ($(CONFIG_INSTALL_DEBIAN_KERNEL_PACKAGE),y)
   ALL_TARGETS += debian
endif
ALL_TARGETS += debootstrap prepare_sdcard


all: $(ALL_TARGETS)
	@echo "Done. You can now use your $(CONFIG_BOARD) :)"


.PHONY: help

help:
	@echo "What you can do:"
	@echo
	@echo "install-deps.....: Install requirements for your platform"
	@echo "menuconfig.......: Starts the configuration menu. Output is stored as .config."
	@echo "init.............: Intializes repo with a manifest (implicitely selected)."
	@echo "sync.............: Fetches all sources mentioned by the manifest file."
	@echo "all [default]....: Generates the image by proceeding all the build steps."
	@echo
	@echo
	@echo "  -- Kernel --"
	@echo "linux............: Compiles Linux: generates uImage and DTB."
	@echo "linux-config.....: Copy environment KERNEL_CONFIG as .config."
	@echo "linux-defconfig..: Pass to Linux a default configuration."
	@echo "linux-<TARGET>...: Will call <TARGET> in the linux directory. E.g linux-menuconfig."
	@echo
	@echo " -- U-Boot --"
	@echo "u-boot...........: Compiles U-Boot."
	@echo "u-boot-<TARGET>..: Will call <TARGET> in the U-Boot directory."
	@echo
	@echo "  -- Packaging --"
	@echo "debian...........: Generated Debian packages of the Kernel."
	@echo
	@echo "  -- Rootfs & Image --"
	@echo "debootstrap......: Create the root_fs via debootstrap."
	@echo "prepare_sdcard...: Creates a flashable image."
	@echo
	@echo "  -- Cleaning --"
	@echo "clean............: Run clean in linux and u-boot. Remove generated files."
	@echo "distclean........: Run distclean in linux and u-boot. Remove build directory."
	@echo "mrproper.........: Remove everything that was generated or fetched"
	@echo "repo-clean.......: Remove sources fetched by repo"
	@echo "debootstrap-clean: Remove the rootfs created by debootstrap"
	@echo


.PHONY: debian

debian: board-config-required $(DEPS) linux-defconfig linux
	$(SCRIPTS_DIR)/make_debian_packages.sh

boot.cmd: $(DEPS) boot.cmd.in
	$(SED) \
	   -e 's|@DTB@|$(CONFIG_DTB)|g' \
	   -e 's|@ROOTFS@|$(CONFIG_ROOTFS)|g' \
	   -e 's|@CONFIG_EXTRA_BOOTARGS@|$(patsubst "%",%,$(CONFIG_EXTRA_BOOTARGS))|g' \
	   boot.cmd.in > $@


.PHONY: debootstrap debootstrap-clean prepare_sdcard

debootstrap: board-config-required $(DEPS) boot.cmd
	$(SCRIPTS_DIR)/make_debootstrap.sh all

debootstrap-clean: $(MAKEFILE_DEPS)
	sudo $(RM) -r $(CHROOT_DIR)

prepare_sdcard: board-config-required $(DEPS)
	$(SCRIPTS_DIR)/prepare_sdcard.sh all


.PHONY: clean

clean: $(MAKEFILE_DEPS)
	$(MAKE) $(call clean-targets,$@)
	$(RM) boot.cmd

.PHONY: distclean

distclean: $(MAKEFILE_DEPS) clean debootstrap-clean
	$(MAKE) $(call clean-targets,$@)
	$(RM) -r $(BUILD_DIR)
	$(RM) $(CONFIG)

.PHONY: mrproper

mrproper: $(MAKEFILE_DEPS) distclean repo-clean
	$(MAKE) $(call clean-targets,$@)
	if [ -d .git/ ]; then git clean -dfx; fi


.PHONY: init sync repo-clean

init: config-required $(DEPS)
	$(PYTHON2) $$(which repo) init -u $(MANIFESTS_URL) -m $(CONFIG_BOARD)/$(CONFIG_MANIFEST) -b $(MANIFESTS_REVISION)

sync: config-required $(DEPS)
	$(PYTHON2) $$(which repo) sync

repo-clean:
	$(RM) -r .repo

.PHONY: install-deps

install-deps:
	./scripts/install-deps

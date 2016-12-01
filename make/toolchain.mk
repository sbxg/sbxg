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

ARCH := $(shell uname --machine)

TC_VERSION := 6.1.1-2016.08
TC_BASE_URL := https://releases.linaro.org/components/toolchain/binaries
TC_VERSION := 6.2-2016.11
TC_EABI := arm-linux-gnueabihf
TC_GCC := gcc-linaro
TC_GCC_VERSION := 6.2.1-2016.11
TC_DIR := $(TC_GCC)-$(TC_GCC_VERSION)-$(ARCH)_$(TC_EABI)
TC_PATH := $(BUILD_DIR)/$(TC_DIR)/bin

TC_URL := $(TC_BASE_URL)/$(TC_VERSION)/$(TC_EABI)/$(TC_DIR).tar.xz

# If the toolchain prefix is manually overriden, then use the user input,
# otherwise use our downloaded EABI
ifeq ($(CONFIG_TOOLCHAIN_PREFIX_CHOICE),)
   TOOLCHAIN_PREFIX := $(TC_EABI)-
else
   TOOLCHAIN_PREFIX := $(CONFIG_TOOLCHAIN_PREFIX)
endif

ifeq ($(CONFIG_TOOLCHAIN_AUTOMATIC),y)
   TOOLCHAIN_DEPS := $(BUILD_DIR)/$(TC_DIR)/bin/$(TOOLCHAIN_PREFIX)gcc
else
   TOOLCHAIN_DEPS :=
endif

.PHONY: toolchain

$(TOOLCHAIN_DEPS):
	$(SHELL) $(SCRIPTS_DIR)/get_toolchain.sh \
	   $(TC_URL) \
	   $(BUILD_DIR) \
	   $(TC_DIR)

toolchain: $(TOOLCHAIN_DEPS)

toolchain-clean: $(DEPS)
	$(Q)$(RM) -r $(BUILD_DIR)/$(TC_DIR)

# This macro prepends to the PATH the path of the toolchain
define toolchain-path
PATH=$(realpath $(TC_PATH)):$(PATH)
endef

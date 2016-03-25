# Copyright (c) 2016, Jean Guyomarc'h <jean.guyomarch@gmail.com>
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

.PHONY: linux linux-%

# Get dts file from dtb to be generated
DTS := $(patsubst %.dtb,%.dts,$(CONFIG_DTB))

# Executes $(1) in the linux directory with JOBS, ARCH and CROSS_COMPILE
# set to the values defined in the configuration
linux-make = $(MAKE) -C $(LINUX_DIR) -j $(CONFIG_JOBS) CROSS_COMPILE=$(CONFIG_GCC_PREFIX) ARCH=arm $(1)

linux: $(DEPS) $(LINUX_DIR)/arch/arm/boot/uImage $(LINUX_DIR)/arch/arm/boot/dts/$(CONFIG_DTB)

$(LINUX_DIR)/arch/arm/boot/uImage: $(DEPS) $(LINUX_DIR)/.config
# extract current SHA1 from git linux kernel version source
# and append this version to the kernel version in order to have this SHA1
# matched in command : uname -a command and SNMP MIB
	EXTRAVERSION=$(call git-hash-get,$(LINUX_DIR)) \
	LOADADDR="$(CONFIG_LOADADDR)" \
	DISABLE_PAX_PLUGINS="$(CONFIG_DISABLE_PAX_PLUGINS)" \
	    $(call linux-make,uImage modules)

$(LINUX_DIR)/arch/arm/boot/dts/$(CONFIG_DTB): $(DEPS) $(LINUX_DIR)/arch/arm/boot/dts/$(DTS) $(LINUX_DIR)/.config
	$(call linux-make,dtbs)

linux-config: $(DEPS)
	cp "$(KERNEL_CONFIG)" $(LINUX_DIR)/.config

$(LINUX_DIR)/.config:
	$(MAKE) linux-defconfig

linux-defconfig: $(DEPS)
ifeq ($(findstring .config,$(wildcard $(LINUX_DIR)/.config)), ) # check if .config can be erased, else do not erase it
	if [ -f $(KERNEL_CONFIGS_DIR)/$(CONFIG_BOARD)/defconfig ]; then \
	 cp $(KERNEL_CONFIGS_DIR)/$(CONFIG_BOARD)/defconfig $(LINUX_DIR)/.config ; \
	 $(call linux-make,olddefconfig); \
	else \
	 $(call linux-make,defconfig); \
	fi ;
else
	@echo "File .config already exists."
endif


# Handle all default targets
linux-%: $(DEPS)
	$(call linux-make,$(patsubst linux-%,%,$@))

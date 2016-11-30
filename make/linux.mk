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

.PHONY: linux linux-%

# Get dts file from dtb to be generated
DTS := $(patsubst %.dtb,%.dts,$(CONFIG_DTB))

ifeq ($(CONFIG_LOADADDR),)
   LINUX_IMAGE_TARGET := linux-zimage
else
   LINUX_IMAGE_TARGET := linux-uimage
endif

# Executes $(1) in the linux directory with JOBS, ARCH and CROSS_COMPILE
# set to the values defined in the configuration
# Custom make environment variables are in $(2)
linux-make = \
   $(call toolchain-path) \
   $(MAKE) \
   EXTRAVERSION=-$(call git-hash-get,$(LINUX_DIR)) \
   DISABLE_PAX_PLUGINS=$(CONFIG_DISABLE_PAX_PLUGINS) \
   $(2) \
   -C $(LINUX_DIR) \
   -j $(CONFIG_JOBS) \
   CROSS_COMPILE=$(TOOLCHAIN_PREFIX) \
   ARCH=arm \
   $(1)

linux: $(DEPS) $(LINUX_IMAGE_TARGET) \
   $(LINUX_DIR)/arch/arm/boot/dts/$(CONFIG_DTB)

linux-zimage: $(LINUX_DIR)/arch/arm/boot/zImage

linux-uimage: $(LINUX_DIR)/arch/arm/boot/uImage

$(LINUX_DIR)/arch/arm/boot/zImage: board-config-required $(DEPS) $(LINUX_DIR)/.config
	targets="zImage"; \
	if grep -q "CONFIG_MODULES=y" $(LINUX_DIR)/.config ; then \
	 targets="$$targets modules"; \
	fi; \
	$(call linux-make,$$targets)

$(LINUX_DIR)/arch/arm/boot/uImage: board-config-required $(DEPS) $(LINUX_DIR)/.config
	targets="uImage"; \
	if grep -q "CONFIG_MODULES=y" $(LINUX_DIR)/.config ; then \
	 targets="$$targets modules"; \
	fi; \
	$(call linux-make,$$targets,LOADADDR=$(CONFIG_LOADADDR))

$(LINUX_DIR)/arch/arm/boot/dts/$(CONFIG_DTB): board-config-required \
   $(DEPS) $(LINUX_DIR)/arch/arm/boot/dts/$(DTS) $(LINUX_DIR)/.config
	$(call linux-make,dtbs)

linux-config: board-config-required $(DEPS)
	cp "$(KERNEL_CONFIG)" $(LINUX_DIR)/.config

$(LINUX_DIR)/.config: board-config-required
	$(MAKE) linux-defconfig

linux-defconfig: board-config-required $(DEPS)
ifeq ($(findstring .config,$(wildcard $(LINUX_DIR)/.config)), ) # check if .config can be erased, else do not erase it
	if [ -f $(CONFIG_KERNEL_CONFIGS_DIR)/$(CONFIG_DEFCONFIG) ]; then \
	 cp $(CONFIG_KERNEL_CONFIGS_DIR)/$(CONFIG_DEFCONFIG) $(LINUX_DIR)/.config ; \
	 $(call linux-make,olddefconfig); \
	else \
	 $(call linux-make,defconfig); \
	fi ;
else # .config exists
	@echo "File .config already exists."
endif # .config nonexistant

linux-menuconfig: board-config-required $(DEPS)
	$(call linux-make,menuconfig)

# Forward targets to linux
linux-%: board-config-required $(DEPS)
	$(call linux-make,$(patsubst linux-%,%,$@),)

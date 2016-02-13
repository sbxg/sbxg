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


.PHONY: u-boot u-boot-%

# Executes $(1) in the u-boot directory with JOBS and CROSS_COMPILE
# set to the values defined in the configuration
u-boot-make = $(MAKE) -C $(UBOOT_DIR) CROSS_COMPILE=$(CONFIG_GCC_PREFIX) -j $(CONFIG_JOBS) $(1)

u-boot: $(DEPS) $(UBOOT_DIR)/$(CONFIG_UBOOT_BIN_NAME)

$(UBOOT_DIR)/$(CONFIG_UBOOT_BIN_NAME):
	$(call u-boot-make,$(CONFIG_BOARD)_config)
	$(call u-boot-make)

# Catch all u-boot targets that were not overriden above
u-boot-%: $(DEPS)
	$(call u-boot-make,$(patsubst u-boot-%,%,$@))

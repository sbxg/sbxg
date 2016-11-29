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

.PHONY: busybox busybox-%

busybox-make = \
   $(call toolchain-path) \
   $(MAKE) -j $(CONFIG_JOBS) -C $(BUSYBOX_DIR) \
   O=../$(BUSYBOX_BUILD_DIR) \
   CROSS_COMPILE=$(TOOLCHAIN_PREFIX) \
   ARCH=arm \
   $(1)

$(BUSYBOX_BUILD_DIR):
	$(Q)mkdir -p $@

busybox-%: $(BUSYBOX_BUILD_DIR) $(DEPS)
	$(call busybox-make,$(patsubst busybox-%,%,$@))

busybox: $(BUSYBOX_BUILD_DIR) $(DEPS)
	$(call busybox-make,busybox)
	$(call busybox-make,install)
	$(SHELL) $(SCRIPTS_DIR)/create_initramfs.sh \
	   $(BUSYBOX_BUILD_DIR) \
	   $(BUILD_DIR)/initramfs.cpio

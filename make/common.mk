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


# Support for quiet/verbose make
# Prefix commands by $(Q) to hide them by default, and enable
# them when providing V=1 to make
ifeq ($(V),)
   V := 0
else
   V := 1
endif
Q_0 := @
Q_1 :=
Q   := $(Q_$(V))


# Extract the git hash (short version) from a git repository specified
# as $(1)
define git-hash-get
$(shell \
   git_dir="$(1)/.git"; \
   if [ -d "$$git_dir" ]; then \
      git --git-dir "$$git_dir" rev-parse --short HEAD; \
   fi
)
endef

.PHONY: config-required

config-required:
ifneq ($(HAS_CONFIG),y)
	$(error No configuration found. Please run 'make menuconfig')
endif


.PHONY: board-config-required

board-config-required: $(REPO_STAMP)

$(REPO_STAMP): $(CONFIG)
ifneq ($(HAS_CONFIG),y)
	$(error No configuration found. Please run 'make menuconfig')
else
	@echo "Configuration changed. Reloading repo..."
	$(MAKE) init
	$(MAKE) sync
	@touch $@
endif

clean-targets = $(1)
ifeq ($(HAS_BOARD_CONFIG),y)
   clean-targets += u-boot-$(1) linux-$(1)
endif

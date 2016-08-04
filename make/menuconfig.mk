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


$(MENUCONFIG_BUILD_DIR):
	$(Q)mkdir -p $@

$(CONF_BUILD_DIR):
	$(Q)mkdir -p $@

$(MENUCONFIG_BUILD_DIR)/Makefile: $(MENUCONFIG_BUILD_DIR)
	$(Q)cmake -H$(MENUCONFIG_DIR) -B$(MENUCONFIG_BUILD_DIR)

$(MENUCONFIG_DIR)/CMakeLists.txt:
	$(Q)git submodule update --init $(MENUCONFIG_DIR)


$(MCONF): $(MENUCONFIG_DIR)/CMakeLists.txt $(MENUCONFIG_BUILD_DIR)/Makefile
	$(Q)$(MAKE) -C $(MENUCONFIG_BUILD_DIR)

$(CONFIG):
	$(MAKE) menuconfig

$(MANIFEST_CFG) $(KERNEL_CONFIGS_CFG): $(CONF_BUILD_DIR)
	$(Q)$(PYTHON) $(SCRIPTS_DIR)/gen_extra_config.py $(MANIFESTS_URL) \
	   $(MANIFEST_CFG) $(KERNEL_CONFIGS_CFG)


# This macro takes a configuration parameter as a first argument and
# generates a Kconfig from it.
# All backslashes are escaped because this macro will be expanded twice
define generate-config
config $(1)\\n \
\\tstring\\n \
\\tdefault \"$(call $(1))\"\\n
endef

# This macro takes all the variables mentioned in EXPORTED_VARIABLES
# and pass them to generate-config to generate a Kconfig block
# for each of these variables
define generate-extra-config
$(foreach var,$(EXPORTED_VARIABLES),$(call generate-config,$(var)))
endef

$(OPENCONF_CFG): $(OPENCONF_CFG_IN) $(MCONF) Makefile makefile.vars
	$(Q)$(SED) \
	   -e "s|@MANIFEST_CFG@|$$(basename $(MANIFEST_CFG))|g" \
	   -e "s|@KERNEL_CONFIGS_CFG@|$$(basename $(KERNEL_CONFIGS_CFG))|g" \
	   -e "s|@PARALLEL_JOBS@|$$(( $$(nproc) + 1 ))|g" \
	   -e "s|@EXTRA_CONFIG@|$(call generate-extra-config)|g" \
	   $< > $@
	$(Q)if [ -f "$(CONFIG)" ]; then $(CONF) --oldconfig $@; fi

.PHONY: menuconfig

menuconfig: $(MCONF) $(MANIFEST_CFG) $(OPENCONF_CFG)
	$(Q)KCONFIG_CONFIG=$(CONFIG) $(MCONF) $(OPENCONF_CFG)


.PHONY: openconf

openconf: $(OPENCONF_CFG)

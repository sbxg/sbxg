# Copyright (c) 2013-2014, Sylvain Leroy <sylvain@unmondelibre.fr>
#                    2014, Jean-Marc Lacroix <jeanmarc.lacroix@free.fr>
#                    2015, Jean Guyomarc'h <jean.guyomarch@gmail.com>
#                    2015, Damien Pradier <damien.pradier@epita.fr>

# This file is part of CBoard.

# CBoard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# CBoard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with CBoard.  If not, see <http://www.gnu.org/licenses/>.

SED := sed
SCRIPTS_DIR := scripts
DEPS := makefile.vars Makefile

export

# makefile.vars is automatically generated by this Makefile. Therefore it
# does not exist at the first execution of make. The "-" before include
# means "don't complain if the file is non-existant".
# When a target needs makefile.vars, this Makefile launches the script
# that generated makefile.vars. At the end of this target, make restarts
# itself and tries again to include makefile.vars. But this time, it exists
# therefore everything can work as expected :)
-include makefile.vars

.PHONY: help all \
   kernel_menuconfig config kernel_gconfig kernel_defconfig kernel_compile  \
   with_grsecurity with_lesser_grsecurity u-boot debootstrap prepare_sdcard \
   check kernel_clean kernel_distclean clean distclean debian kernel_config \
   init sync

help: $(DEPS)
	@echo "What you can do:"
	@echo
	@echo "all:			Will do all the job for you."
	@echo
	@echo "config:                  Generate a user config from the template"
	@echo
	@echo "  -- kernel configuration --"
	@echo "kernel_config:		copies the kernel configuration file specified in config.user as the effective .config"
	@echo "kernel_defconfig:	Write the default kernel configuration for cubieboard or cubieboard2"
	@echo "kernel_menuconfig:	make menuconfig in LINUX_DIR"
	@echo "kernel_gconfig:		make gconfig in LINUX_DIR"
	@echo
	@echo "  -- kernel compilation --"
	@echo "kernel_compile:		make ARCH=arm CROSS_COMPILE=$(GCC_PREFIX) uImage modules"
	@echo "with_grsecurity:	make ARCH=arm CROSS_COMPILE=$(GCC_PREFIX) uImage modules"
	@echo "with_lesser_grsecurity:	make ARCH=arm CROSS_COMPILE=$(GCC_PREFIX) DISABLE_PAX_PLUGINS=y uImage modules"
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
	@echo "  -- checking targets --"
	@echo "check:			Use qemu to check the generated image"
	@echo "			$(QEMU_SYSTEM_ARM) -machine cubieboard -m $(QEMU_MEMORY_SIZE) -nographic -serial stdio -kernel $(LINUX_DIR)/arch/arm/boot/uImage -append \"root=/dev/mmcblk0p1 rootwait panic=10\""
	@echo
	@echo "  -- cleaning targets --"
	@echo "kernel_clean:		"
	@echo "kernel_distclean:	"
	@echo "clean:			clean the compiled files (not done yet)"
	@echo "distclean:		clean the compilet files and the root_fs"
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
	@echo "	FORMAT_SDCARD		=	$(FORMAT_SDCARD)"
	@echo "	SDCARD_DEVICE		=	$(SDCARD_DEVICE)"
	@echo
	@echo "	You can and MUST configure these variables from the file : makefile.vars"
	@echo

all: $(DEPS) u-boot kernel_defconfig kernel_compile debootstrap prepare_sdcard
	@echo "Done. You can now use your $(BOARD_NAME) :)"

config.user: config.template
	cp $< $@

makefile.vars: config.user
	$(SCRIPTS_DIR)/genvars.sh

config: config.user

# Kernel compile

kernel_config: $(DEPS)
	cp "$(KERNEL_CONFIG)" $(LINUX_DIR)/.config

kernel_defconfig: $(DEPS)
ifeq ($(findstring .config,$(wildcard $(LINUX_DIR)/.config)), ) # check if .config can be erased, else do not erase it
	cd $(LINUX_DIR) && make ARCH=arm CROSS_COMPILE=$(GCC_PREFIX) $(KERNEL_DEFCONFIG)
else
	@echo "File .config already exists."
endif

kernel_menuconfig: $(DEPS)
	cd $(LINUX_DIR) && make ARCH=arm CROSS_COMPILE=$(GCC_PREFIX) menuconfig

kernel_gconfig: $(DEPS)
	cd $(LINUX_DIR) && make ARCH=arm CROSS_COMPILE=$(GCC_PREFIX) gconfig

kernel_compile: $(DEPS) $(LINUX_DIR)/arch/arm/boot/uImage $(LINUX_DIR)/arch/arm/boot/dts/$(DTB)

$(LINUX_DIR)/arch/arm/boot/uImage: $(DEPS) $(LINUX_DIR)/.config
# extract current SHA1 from git linux kernel version source
# and append this version to the kernel version in order to have this SHA1
# matched in command : uname -a command and SNMP MIB
	cd $(LINUX_DIR) && make \
	EXTRAVERSION=-`git rev-parse --short HEAD` \
	ARCH=arm \
	CROSS_COMPILE=$(GCC_PREFIX) \
	-j $(JOBS) \
	DISABLE_PAX_PLUGINS=y \
	uImage modules LOADADDR=$(LOADADDR)

$(LINUX_DIR)/arch/arm/boot/dts/$(DTB): $(DEPS) $(LINUX_DIR)/arch/arm/boot/dts/$(DTS) $(LINUX_DIR)/.config
	cd $(LINUX_DIR) && make \
	EXTRAVERSION=-`git rev-parse --short HEAD` \
	ARCH=arm \
	CROSS_COMPILE=$(GCC_PREFIX) \
	-j $(JOBS) \
	DISABLE_PAX_PLUGINS=y \
	dtbs LOADADDR=$(LOADADDR)

# with_grsecurity:
# 	cd $(LINUX_DIR) && make ARCH=arm CROSS_COMPILE=$(GCC_PREFIX) -j $(JOBS) uImage modules

# with_lesser_grsecurity:
# 	cd $(LINUX_DIR) && make ARCH=arm CROSS_COMPILE=$(GCC_PREFIX) DISABLE_PAX_PLUGINS=y -j $(JOBS) uImage modules

kernel_clean: $(DEPS)
	cd $(LINUX_DIR) && make CROSS_COMPILE=$(GCC_PREFIX) clean

kernel_distclean: $(DEPS)
	cd $(LINUX_DIR) && make CROSS_COMPILE=$(GCC_PREFIX) mrproper

# make-kpkg

debian: $(DEPS)
	$(SCRIPTS_DIR)/make_debian_packages.sh $(LINUX_DEBIAN_PACKAGES)


# bootloader u-boot compile

u-boot: $(DEPS) $(UBOOT_DIR)/u-boot-sunxi-with-spl.bin

$(UBOOT_DIR)/u-boot-sunxi-with-spl.bin:
	cd $(UBOOT_DIR) && make CROSS_COMPILE=$(GCC_PREFIX) -j $(JOBS) $(BOARD_NAME)_config
	cd $(UBOOT_DIR) && make CROSS_COMPILE=$(GCC_PREFIX) -j $(JOBS)

u-boot_clean: $(DEPS)
	cd $(UBOOT_DIR) && make CROSS_COMPILE=$(GCC_PREFIX) clean

u-boot_distclean: $(DEPS)
	cd $(UBOOT_DIR) && make CROSS_COMPILE=$(GCC_PREFIX) distclean

# Debootstrap

boot.cmd: $(DEPS) boot.cmd.in
	$(SED) 's/@DTB@/$(DTB)/g' boot.cmd.in > $@

debootstrap: $(DEPS) boot.cmd
	$(SCRIPTS_DIR)/make_debootstrap.sh all

prepare_sdcard: $(DEPS)
	$(SCRIPTS_DIR)/prepare_sdcard.sh all

# Check

check: $(DEPS) $(LINUX_DIR)/arch/arm/boot/uImage
	$(QEMU_SYSTEM_ARM) -machine cubieboard -m $(QEMU_MEMORY_SIZE) -nographic -serial stdio -kernel $(LINUX_DIR)/arch/arm/boot/uImage -append "root=/dev/mmcblk0p1 rootwait panic=10"

# Cleaning stuff

clean: $(DEPS) u-boot_clean kernel_clean
	$(RM) makefile.vars
	$(RM) config.user
	$(RM) .board


distclean: $(DEPS) clean u-boot_distclean kernel_distclean
	sudo $(RM) -r $(CHROOT_DIR)

init:
ifeq ($(BOARD),)
	@echo "*** You need to provide the board via 'make BOARD=xxx init'"
else
	# Keep track of the board name, to be able to source the config later
	echo "$(BOARD)" > .board
	repo init -u git@gitlab.users.showroom.nss.thales:systembuilder-ng/manifests.git -m "$(BOARD)/linux.xml"
endif

sync:
	repo sync
	$(SCRIPTS_DIR)/genvars.sh


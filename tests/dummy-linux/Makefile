all: arch/arm/boot/dts/dummy.dtb arch/arm/boot/uImage arch/arm/boot/zImage

arch/arm/boot/dts/dummy.dtb: arch/arm/boot/dts/dummy.dts
	@echo "  (GEN) $@"
	touch $@

arch/arm/boot/uImage arch/arm/boot/zImage:
	@echo "  (GEN) $@"
	touch $@

clean distclean mrproper:
	@echo "  (CLEAN) $@"
	$(RM) arch/arm/boot/uImage
	$(RM) arch/arm/boot/zImage
	$(RM) arch/arm/boot/dts/dummy.dtb

dtbs: arch/arm/boot/dts/dummy.dtb

uImage: arch/arm/boot/uImage

zImage: arch/arm/boot/zImage

olddefconfig defconfig menuconfig modules modules_install:
	@echo "  (STUB) $@"

.PHONY: \
   clean all olddefconfig defconfig menuconfig dtbs modules \
   modules_install uImage zImage

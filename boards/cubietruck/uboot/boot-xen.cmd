# SUNXI Xen Boot Script


# Requirements for this script to work
# (you can use symbolic links to point to the correct file) :
# - recent enough u-boot to support the bootz command
# - Xen Kernel using the zImage (default in Debian package) format at /boot/xen
# - Kernel using the zImage format at /boot/zImage
# - Initrd using the initramfs format at /boot/initrd
#   (example for debian the update-initramfs command can be used to create it)
# - DTB using the device-tree binary format provided by the kernel at /boot/dtb
#   (for example, if using a Debian Kernel package, look for the dtb
#   corresponding to your board in /usr/lib/KERNEL_NAME/)

# Top of RAM:         0xc0000000
# Xen relocate addr   0xbfe00000 # 2M
setenv kernel_addr_r  0xbf600000 # 8M
setenv ramdisk_addr_r 0xbc200000 # 100M
setenv fdt_addr       0xbc000000 # 2M
setenv xen_addr_r     0xbbe00000 # 2M

setenv fdt_high       0xffffffff # Load fdt in place instead of relocating

# Load  xen/xen  to ${xen_addr_r}. e.g.  tftp,  fatload or ext2load to
# ${xen_addr_r}.   see the following  sections  for details of booting
# from various devices.

fatload mmc 0 ${xen_addr_r} {{ board.xen_image }}

setenv bootargs "console=dtuart dtuart=/soc@01c00000/serial@01c28000 dom0_mem=512M flask=disabled guest_loglvl=all loglvl=all iommu=debug"

# Load  appropriate .dtb file to   ${fdt_addr}  e.g. tftp, fatload  or
# ext2load to ${fdt_addr}.  see  the following sections for details of
# booting from various devices.

fatload mmc 0 ${fdt_addr} {{ board.linux_dtb }}

fdt addr ${fdt_addr} 0x40000

fdt resize

fdt chosen

fdt set /chosen \#address-cells <1>
fdt set /chosen \#size-cells <1>

# Load Linux  arch/arm/boot/zImage  to  ${kernel_addr_r}.  e.g.  tftp,
# fatload or ext2load to ${kernel_addr_r}.  see the following sections
# for details of booting from various devices.

fatload mmc 0 ${kernel_addr_r} {{ board.linux_image }}

fdt mknod /chosen module@0
fdt set /chosen/module@0 compatible "xen,linux-zimage" "xen,multiboot-module"
fdt set /chosen/module@0 reg <${kernel_addr_r} 0x${filesize}>
fdt set /chosen/module@0 bootargs "earlyprintk console=hvc0 disp.screen0_output_type=3 root={{ board.root }} clk_ignore_unused rootwait ${extra}"

bootz ${xen_addr_r} - ${fdt_addr}

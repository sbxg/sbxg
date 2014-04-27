#! /usr/bin/env sh

#set -x
set -e

#############
# VARIABLES #
#############

# internal values
BUILD_SERIAL=`date "+%Y%m%d%H%M"`
TMP_VAL=$$
DD_TIMEOUT=5

# Including users defined variables
. ./makefile.vars

# user defined values
IMG_SIZE=2048
CONF_SIZE=50
PARTITION_SIZE=$((($IMG_SIZE - $CONF_SIZE) / 2))
FS_TYPE=ext2
IMG_NAME="$CUBIEBOARD_VERSION"-"$BUILD_SERIAL"-"$IMG_SIZE".img
EXIT_ERROR=1
EXIT_OK=0

############
# FUNCTION #
############

build_image()
{
set -e

# first  step, create a  local file and init it with  NULL values,
# please note that potential error (disk full) is trapped (set -e)

if [ ! -e "$IMG_NAME" ]; then
    # Start dd in background to be able to print its progress waiting it to finish
    dd if=/dev/zero of="$IMG_NAME" bs=1M count="$IMG_SIZE" iflag=fullblock &
    # While dd is still running, show it's progress
    while ps -p $! > /dev/null ; do
	kill -USR1 "$!"
	sleep "$DD_TIMEOUT"
    done
fi

# second step, create  3 partitions in  this image, the first  one for
# boot software, the second for rootfs and the  last for FIXME. Please
# note that alignment is done on multiple of IMG_SIZE

/sbin/parted --script "$IMG_NAME" mklabel msdos
/sbin/parted --script --align optimal "$IMG_NAME" mkpart primary 1 $(($PARTITION_SIZE + 1))
/sbin/parted --script --align optimal "$IMG_NAME" mkpart primary $(($PARTITION_SIZE + 2)) $((($PARTITION_SIZE * 2) + 1))
/sbin/parted --script --align optimal "$IMG_NAME" mkpart primary $((($PARTITION_SIZE * 2) + 2)) $IMG_SIZE

# for each  internal partition in the  file, create  one device in the
# kernel on the loopback (/dev/loopxxxx), so that it is later possible
# to mount it as valid file system.  Please  note that this feature is
# available only if  your  running kernel  has  'kernel device mapper'
# feature. Furthermore, the loop device  is not static, but depends of
# current kernel configuration.  This  is why output of command kpartx
# must be parsed in  order to discover real  loop device number (  For
# exemple, if your running kernel use raid and lvm devices)

# !!! why do we remove error checking? !!!
set +e
RES=`sudo /sbin/kpartx -a -v -p "$TMP_VAL" "$IMG_NAME"`
if [ $? -ne 0 ]; then
	# some time, error  when using kpartx,  probably bad free internal
	# loop  ressource, look at following error....
	# mount: could  not find any free loop deviceBad address
	# can't set up loop
	echo "error when launching : sudo /sbin/kpartx -a -v -p $TMP_VAL $IMG_NAME"
	exit $EXIT_ERROR
fi
set -e
# now manage  output of command, we try  to extract the correct device
# number for the loop device as in following exemple (/dev/loop0)
# sudo /sbin/kpartx -a -v -p 22157 cubieboard2-201404090807-248.img
# add map loop0221571 (253:73): 0 192512 linear /dev/loop0 2048
# add map loop0221572 (253:74): 0 192512 linear /dev/loop0 196608
# add map loop0221573 (253:75): 0 96256 linear /dev/loop0 389120

MY_LOOP_DEV=`echo $RES |awk '{print $8}'`
MY_LOOP_DEV=`basename $MY_LOOP_DEV`

# add current process id to loopdev
LOOP_DEV=/dev/mapper/"$MY_LOOP_DEV""$TMP_VAL"

if [ -b "$LOOP_DEV"1 ]; then
    sudo /sbin/mkfs."$FS_TYPE" "$LOOP_DEV"1
fi
if [ -b "$LOOP_DEV"2 ]; then
    sudo /sbin/mkfs."$FS_TYPE" "$LOOP_DEV"2
fi
if [ -b "$LOOP_DEV"3 ]; then
    sudo /sbin/mkfs."$FS_TYPE" "$LOOP_DEV"3
fi

# free internal loop device ...
sudo /sbin/kpartx -d -p "$TMP_VAL" "$IMG_NAME"

# print image output for human checking purpose
sudo /sbin/parted "$IMG_NAME" print
}

########

copyboot2image()
{
# copy boot binaries to the image
    # Should match a device regexp or something like that.
    if [ -n "$IMG_NAME" ]; then
	if [ -f "$IMG_NAME" ]; then
	    if [ -f u-boot-sunxi/spl/sunxi-spl.bin ]; then
			# copy previously generated u-boot files on image
			sudo dd \
				if=u-boot-sunxi/spl/sunxi-spl.bin \
				of="$IMG_NAME" \
				bs=1024 \
				seek=8 \
				conv=nocreat,notrunc
	    else
			echo "You need to build u-boot first"
			exit $EXIT_ERROR
	    fi
	    if [ -f u-boot-sunxi/u-boot.bin ]; then
			sudo dd \
				if=u-boot-sunxi/u-boot.bin \
				of="$IMG_NAME" \
				bs=1024 \
				seek=32 \
				conv=nocreat,notrunc
	    else
			echo "You need to build u-boot first"
			exit $EXIT_ERROR
	    fi
	else
	    echo "$IMG_NAME does not seem to be a regular image file..."
		exit $EXIT_ERROR
	fi
    else
		echo "The variable IMG_NAME does not seem to exist..."
		exit $EXIT_ERROR
    fi
}

########

copyrootfs2image()
{
# copy root_fs to the image
    # Should match a device regexp or something like that.
    set +e
    sudo /sbin/kpartx -a -v -p "$TMP_VAL" "$IMG_NAME"
    if [ -n "$LOOP_DEV"1 ] ;then
		if [ -b "$LOOP_DEV"1 ] ;then
            # CHROOT_DIR      is  created        when   launching
            # make_debootstrap.sh, so if not done, not possible to make
            # cd  "$CHROOT_DIR" because not  existant,  and we must be
            # sure to mount device, otherwise not  possible to
            # free loop device later because 'in used by mount'
			if [ -d "$CHROOT_DIR" ] ;then
				cd "$CHROOT_DIR"
				sudo mount "$LOOP_DEV"1 /mnt
				sudo bash -c "tar --exclude=qemu-arm-static -cf - . | tar -C /mnt -xvf -"
				cd ..
				sudo umount /mnt
			else
				echo " $CHROOT_DIR not existant, please run make debootstrap first"
				sudo /sbin/kpartx -d -p "$TMP_VAL" "$IMG_NAME"
				exit $EXIT_ERROR
			fi
		else
			echo $LOOP_DEV"1 does not seem to be a block device..."
			sudo /sbin/kpartx -d -p "$TMP_VAL" "$IMG_NAME"
			exit $EXIT_ERROR
		fi
    else
		echo "The variable LOOP_DEV does not seem to exist..."
		sudo /sbin/kpartx -d -p "$TMP_VAL" "$IMG_NAME"
		exit $EXIT_ERROR
    fi
    sudo /sbin/kpartx -d -p "$TMP_VAL" "$IMG_NAME"
    set -e
}

########
# MAIN #
########

case "$1" in
    all)
	build_image
	copyboot2image
	copyrootfs2image
	;;
    build_image)
	build_image
	;;
    copyboot2image)
	copyboot2image
	;;
    copyrootfs2image)
	copyrootfs2image
	;;
    *)
	echo "Usage: prepare_sdcard.sh {all|build_image|copyboot2image|copyrootfs2image}"
	exit $EXIT_ERROR
esac

exit $EXIT_OK

########

setenv bootargs console=ttyS0,115200 root={{ board.root }} earlyprintk ${extra} rootwait
fatload mmc 0 0x46000000 {{ board.linux_image }}
fatload mmc 0 0x49000000 {{ board.linux_dtb }}
bootz 0x46000000 - 0x49000000

"""
    SBXG
    ~~~~

    SBXG is a build system generator designed to build multiple instances of
    the Linux kernel, the U-Boot bootloader and the Xen hypervisor. It can be
    used to generate disk images with these components, given that a foreign
    rootfs is provided to SBXG.

    :copyright: (c) 2017, 2019 by the SBXG Team.
    :license: MIT, see LICENSE for more details.
"""

__docformat__ = 'restructuredtext en'
__version__ = '0.2.99'

from . import cli
from . import library
from . import model
from . import template

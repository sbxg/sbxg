# Copyright (c) 2017, 2019 Jean Guyomarc'h
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pathlib import Path
from urllib.parse import urlparse
import yaml
import cerberus

import sbxg
from sbxg.utils import SbxgError

TOOLCHAIN_SCHEMA = {
    'url': {
        'type': 'string',
        'required': False,
        'default': '',
    },
    'path': {
        'type': 'string',
        'required': True,
    },
    'host': {
        'type': 'string',
        'required': False,
    },
    'arch': {
        'type': 'string',
        'required': False,
        'default': '',
    },
    'xen_arch': {
        'type': 'string',
        'required': False,
        'default': '',
    },
    'prefix': {
        'type': 'string',
        'required': True,
    },
}

SOURCE_SCHEMA = {
    'url': {
        'type': 'string',
        'required': True,
    },
    'path': {
        'type': 'string',
        'required': True,
    },
}

BOARD_SCHEMA = {
    'genimage': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'toolchain': {
        'type': 'string',
        'required': True,
        'empty': True,
    },
    'linux': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'linux_config': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'uboot': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'uboot_config': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'xen': {
        'type': 'string',
        'required': False,
    },
    'xen_config': {
        'type': 'string',
        'required': False,
    },
    'boot_script': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'disk_image': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'linux_dtb': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'linux_image': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'uboot_image': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'root': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'rootfs': {
        'type': 'string',
        'required': True,
        'empty': False,
    },
    'linux_bootargs': {
        'type': 'string',
        'required': False,
    },
}

def _load_config_file(config_file, schema):
    """"
    Load a given yaml file from the filesystem and return the deserialized
    associated data
    """
    with open(config_file, 'r') as stream:
        config_contents = stream.read()
        data = yaml.load(config_contents, Loader=yaml.Loader)

    validator = cerberus.Validator(schema)
    if not validator.validate(data):
        raise SbxgError(f"Failed to parse configuration file "
                        f"'{config_file}': {validator.errors}")
    return validator.normalized(data)


def _url_get_basename(url):
    url_path = Path(urlparse(url).path)
    return url_path.name

def _get_rootfs(url):
    """The rootfs may be specified as a URL or as a path. If it is a path (no
    URL scheme) or if the URL happens to be a local file, then we consider we
    have nothing to download, so we return None as the URL.

    Returns: a tuple (url, path)
    """
    parsed_url = urlparse(url)
    path = Path(parsed_url.path)
    return url, path.name

def _canonicalize(name):
    return name.replace("-", "_").replace(".", "_")

def _set_archive_from_url(obj):
    obj["archive"] = _url_get_basename(obj["url"])


class Model:
    """
    The Model class holds the SBXG configuration. It is an aggregation of
    data models and can be accessed in the same fashion than a dictionary.
    This allows this class to be passed directly to the jinja templating engine
    flawlessly.
    """
    def __init__(self, top_build_dir):
        self.top_build_dir = top_build_dir
        self.toolchain = None
        self.genimage = None
        self.linuxes = []
        self.uboots = []
        self.xens = []
        self.downloads = []
        self.board_info = dict()

    def _add_download(self, name, url, archive):
        item = {
            "name": name,
            "url": url,
            "archive": archive,
        }
        if item not in self.downloads:
            self.downloads.append(item)

    def _load_component(self, config_file, kconfig):
        obj = _load_config_file(config_file, SOURCE_SCHEMA)
        obj["config"] = kconfig
        obj["name"] = _canonicalize(kconfig.name)
        obj["download"] = _canonicalize(config_file.with_suffix("").name)
        _set_archive_from_url(obj)
        self._add_download(obj["download"], obj["url"], obj["archive"])
        return obj

    def set_toolchain(self, config_file):
        """Affect to the current model the toolchain to be used, from a given
        input configuration file

        Args:
            config_file (Path): path to a toolchain configuration file that
                describes the characteristics of the toolchain, and how it
                should be downloaded, if necessary
        """
        self.toolchain = _load_config_file(config_file, TOOLCHAIN_SCHEMA)
        _set_archive_from_url(self.toolchain)
        if "url" in self.toolchain:
            url = self.toolchain["url"]
            archive = self.toolchain["archive"]
            self._add_download("toolchain", url, archive)

    def set_genimage(self, config_file):
        self.genimage = _load_config_file(config_file, SOURCE_SCHEMA)
        _set_archive_from_url(self.genimage)
        url = self.genimage["url"]
        archive = self.genimage["archive"]
        self._add_download("genimage", url, archive)

    def add_linux(self, config_file, kconfig):
        self.linuxes.append(self._load_component(config_file, kconfig))

    def add_uboot(self, config_file, kconfig):
        self.uboots.append(self._load_component(config_file, kconfig))

    def add_xen(self, config_file, kconfig):
        self.xens.append(self._load_component(config_file, kconfig))

    def set_board(self, lib_dirs, config_file):
        """
        From the input configuration file and the SBXG library, set the model's
        fields so each component involved with the board is setup.

        Args:
            lib_dirs (list): List of directories that constitute the SBXG
                library
            config_file (Path): path to the configuration file that descrives
                the board to be generated
        """
        # First, deserialize the board configuration from the Yaml file
        board = _load_config_file(config_file, BOARD_SCHEMA)

        # If the file describes a toolchain, set the model's toolchain
        if "toolchain" in board:
            toolchain = sbxg.utils.get_toolchain(lib_dirs, board["toolchain"])
            self.set_toolchain(toolchain)

        genimage = sbxg.utils.get_genimage_source(lib_dirs, board["genimage"])
        self.set_genimage(genimage)

        # A board always comes with a Linux. Register it.
        linux_src = sbxg.utils.get_linux_source(lib_dirs, board["linux"])
        linux_cfg = sbxg.utils.get_linux_config(lib_dirs, board["linux_config"])
        self.add_linux(linux_src, linux_cfg)

        # A board always comes with a U-Boot. Register it.
        uboot_src = sbxg.utils.get_uboot_source(lib_dirs, board["uboot"])
        uboot_cfg = sbxg.utils.get_uboot_config(lib_dirs, board["uboot_config"])
        self.add_uboot(uboot_src, uboot_cfg)

        rootfs_url, rootfs_path = _get_rootfs(board["rootfs"])

        self.board_info["linux_dtb"] = board["linux_dtb"]
        self.board_info["linux_image"] = board["linux_image"]
        self.board_info["uboot_image"] = board["uboot_image"]
        self.board_info["boot_script"] = board["boot_script"]
        self.board_info["disk_image"] = board["disk_image"]
        self.board_info["root"] = board["root"]
        self.board_info["rootfs_url"] = rootfs_url
        self.board_info["rootfs_path"] = rootfs_path
        self.board_info["linux_bootargs"] = board.get("linux_bootargs", '')

    def context(self):
        return {
            "toolchain": self.toolchain,
            "downloads": self.downloads,
            "linuxes": self.linuxes,
            "xens": self.xens,
            "uboots": self.uboots,
            "top_build_dir": self.top_build_dir,
            "genimage": self.genimage,
            "board": self.board_info,
        }

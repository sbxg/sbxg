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

from . import error as E
from . import utils

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
        raise E.SbxgError(f"Failed to parse configuration file '{config_file}': {validator.errors}")
    return validator.normalized(data)


def _url_get_basename(url):
    url_path = Path(urlparse(url).path)
    return url_path.name

class Database:
    """
    The Database class holds the SBXG configuration. It is an aggregation of
    data models and can be accessed in the same fashion than a dictionary.
    This allows this class to be passed directly to the jinja templating engine
    flawlessly.
    """
    def __init__(self, top_source_dir, top_build_dir):
        self.top_source_dir = top_source_dir
        self.top_build_dir = top_build_dir
        self.toolchain = None
        self.kernel = None
        self.uboot = None
        self.xen = None

    def _set_archive_from_url(self, obj):
        obj["archive"] = _url_get_basename(obj["url"])

    def _load_component(self, config_file, kconfig):
        obj = _load_config_file(config_file, SOURCE_SCHEMA)
        obj["config"] = kconfig
        self._set_archive_from_url(obj)
        return obj

    def set_toolchain(self, config_file):
        self.toolchain = _load_config_file(config_file, TOOLCHAIN_SCHEMA)
        self._set_archive_from_url(self.toolchain)

    def set_kernel(self, config_file, kconfig):
        self.kernel = self._load_component(config_file, kconfig)

    def set_uboot(self, config_file, kconfig):
        self.uboot = self._load_component(config_file, kconfig)

    def set_xen(self, config_file, kconfig):
        self.xen = self._load_component(config_file, kconfig)

    def context(self):
        return {
            "toolchain": self.toolchain,
            "kernel": self.kernel,
            "xen": self.xen,
            "uboot": self.uboot,
            "top_build_dir": self.top_build_dir,
            "top_source_dir": self.top_source_dir,
        }

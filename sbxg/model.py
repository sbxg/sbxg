# Copyright (c) 2017 Jean Guyomarc'h
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

import abc
import collections
import os
import yaml

from . import error as E


class Model(object):
    def __getitem__ (self, attr):
        return getattr(self, attr)

    @abc.abstractproperty
    def config_file(self):
        pass

    @abc.abstractproperty
    def namespace(self):
        pass

    def _yaml_load(self):
        """"
        Load the configuration from a file that is provided through the
        virtual property config_file().
        A dictionary will be returned from the parsed YAML configuration.
        """
        with open(self.config_file(), 'r') as stream:
            config_contents = stream.read()
            return yaml.load(config_contents)

    def check_mandatory(self, element, obj=None):
        obj = self if obj is None else obj
        attr = getattr(obj, element)
        if not attr:
            raise E.MissingRequiredData(self.config_file(),
                                        self.namespace() + element)
        return attr

    def check_mandatory_file(self, element, obj=None):
        obj = self if obj is None else obj
        attr = self.check_mandatory(element, obj)
        if not os.path.isfile(attr):
            raise E.InvalidFileData(self.config_file(),
                                    self.namespace() + key,
                                    attr)

    def check_optional_list(self, element, obj=None):
        obj = self if obj is None else obj
        attr = getattr(obj, element)
        if attr and not isinstance(attr, list):
            raise E.NotAList(self.config_file(),
                             self.namespace() + element)

    def _get_source(self, source, db, key, lib_dirs):
        name = self.get_mandatory(db, key)
        for lib_dir in lib_dirs:
            search = os.path.join(lib_dir, "sources", source, name + ".yml")
            if os.path.isfile(search):
                return search
        raise E.InvalidFileData(self.config_file(),
                                self.namespace() + key,
                                name + ".yml")

    def _get_config(self, config, db, key, lib_dirs):
        name = self.get_mandatory(db, key)
        config_path = os.path.join("configs", config, name)
        for lib_dir in lib_dirs:
            search = os.path.join(lib_dir, config_path)
            if os.path.isfile(search):
                return search
        raise E.InvalidFileData(self.config_file(),
                                self.namespace() + key,
                                config_path)

    def get_mandatory(self, db, attribute):
        if attribute in db:
            return db[attribute]
        raise E.MissingRequiredData(self.config_file(),
                                    self.namespace() + attribute)

    def get_toolchain_source(self, db, key, lib_dirs):
        config_file = self._get_source("toolchain", db, key, lib_dirs)
        toolchain = Toolchain(config_file)
        toolchain.load()
        return toolchain

    def get_kernel_source(self, db, key, lib_dirs, suffix=""):
        config_file = self._get_source("kernel", db, key, lib_dirs)
        kernel = Kernel(config_file, suffix)
        kernel.load()
        return kernel

    def get_uboot_source(self, db, key, lib_dirs):
        config = self._get_source("uboot", db, key, lib_dirs)
        uboot = Uboot(config)
        uboot.load()
        return uboot

    def get_xen_source(self, db, key, lib_dirs):
        config = self._get_source("xen", db, key, lib_dirs)
        xen = Xen(config)
        xen.load()
        return xen

    def get_kernel_config(self, db, key, lib_dirs):
        return self._get_config("kernel", db, key, lib_dirs)

    def get_xen_config(self, db, key, lib_dirs):
        return self._get_config("xen", db, key, lib_dirs)

    def get_uboot_config(self, db, key, lib_dirs):
        return self._get_config("uboot", db, key, lib_dirs)

    def get_bootscript(self, db, key, lib_dirs):
        return self._get_config("bootscripts", db, key, lib_dirs)

    def get_genimage_config(self, db, key, board_dir):
        name = self.get_mandatory(db, key)
        search = os.path.join(board_dir, "images", name)
        if os.path.isfile(search):
            return search
        raise E.InvalidFileData(self.config_file(),
                                self.namespace() + key,
                                search)

    @abc.abstractmethod
    def load(self, lib_dirs, board_dir, **kwargs):
        """
        Load a data model
        Returns: the parse configuration
        """
        pass

class Guest(Model):
    def __init__(self, config_file, parent_toolchain, guest_id):
        self._config_file = config_file
        self.toolchain = parent_toolchain
        self.guest_id = guest_id
        self.kernel = None
        self.linux_image = None
        self.image = None
        self.genimage_config = "genimage_guest{}.cfg".format(self.guest_id)
        super().__init__()

    def load(self, lib_dirs, board_dir, config):
        if "toolchain" in config:
            self.toolchain = self.get_toolchain_source(
                config["toolchain"], lib_dirs
            )
        suffix = "_guest_{}".format(self.guest_id)
        self.kernel = self.get_kernel_source(config, "kernel", lib_dirs, suffix)
        self.kernel.config = self.get_kernel_config(config, "kernel_config", lib_dirs)
        self.linux_image = self.get_mandatory(config, "linux_image")
        self.image = self.get_genimage_config(config, "image", board_dir)
        return config


class Board(Model):
    def config_file(self):
        return self._config_file

    def namespace(self):
        return self._namespace

    def __init__(self, config_file):
        self._config_file = config_file
        self._namespace = "::"
        self.toolchain = None
        self.kernel = None
        self.kernel_config = None
        self.uboot = None
        self.uboot_config = None
        self.boot_script = None
        self.image = None
        self.linux_dtb = None
        self.linux_image = None
        self.uboot_image = None
        self.root = None
        self.templated_boot_script_name = "boot.cmd"
        self.output_boot_script_name = "boot.scr"
        self.xen = None
        self.xen_config = None
        self.xen_image = None
        self.xen_guests = None

    def load(self, lib_dirs, board_dir):
        config = self._yaml_load()

        if not "board" in config:
            raise E.MissingRequiredData(self.config_file(), self.namespace() + "board")

        # Open up the board "namespace"
        db = config["board"]
        self._namespace += "board::"

        self.toolchain = self.get_toolchain_source(db, "toolchain", lib_dirs)
        self.kernel = self.get_kernel_source(db, "kernel", lib_dirs)
        self.kernel_config = self.get_kernel_config(db, "kernel_config", lib_dirs)
        self.uboot = self.get_uboot_source(db, "uboot", lib_dirs)
        self.uboot_config = self.get_uboot_config(db, "uboot_config", lib_dirs)
        self.boot_script = os.path.basename(self.get_bootscript(db, "boot_script", lib_dirs))
        self.image = self.get_genimage_config(db, "image", board_dir)
        self.linux_dtb = self.get_mandatory(db, "linux_dtb")
        self.linux_image = self.get_mandatory(db, "linux_image")
        self.uboot_image = self.get_mandatory(db, "uboot_image")
        self.root = self.get_mandatory(db, "root")
        if "output_boot_script_name" in db:
            self.output_boot_script_name = db["output_boot_script_name"]
        if "xen" in db:
            self.xen = self.get_xen_source(db, "xen", lib_dirs)
            self.xen_config = self.get_xen_config(db, "xen_config", lib_dirs)
            self.xen_image = self.get_mandatory(db, "xen_image")
        if "xen_guests" in db:
            self.xen_guests = []
            for guest_id, xen_guest in enumerate(db["xen_guests"]):
                guest = Guest(self._config_file, self.toolchain, guest_id)
                guest.load(lib_dirs, board_dir, xen_guest)
                self.xen_guests.append(guest)
        return config


class Source(Model):
    def config_file(self):
        return self._config_file

    def namespace(self):
        # Sources have their configuration in the 'global namespace'. It means
        # the properties reside at the top level of the dictionary, there is no
        # nesting.
        return "::"

    def __init__(self, in_file):
        self._config_file = in_file
        self._subconfig = None
        self.path = None
        self.url = None
        self.compression = None
        self.pgp_signature = None
        self.pgp_pubkey = None
        self.sha256 = None
        self.suffix = ""
        self.build_dir = None

    def load(self):
        config = self._yaml_load()
        self.url = self.get_mandatory(config, "url")
        self.path = os.path.abspath(
            self.get_mandatory(config, "path")
        )
        self.sha256 = config.get("sha256")
        self.compressions = config.get("compressions")
        self.pgp_signature = config.get("pgp_signature")
        self.pgp_pubkey = config.get("pgp_pubkey")

        self.build_dir = os.path.join(
            os.path.dirname(self.path),
            "build_" + os.path.basename(self.path) + self.suffix
        )

        self.check_optional_list("compression")
        if self.pgp_signature:
            self.check_mandatory("pgp_pubkey")
        if self.pgp_pubkey:
            self.check_mandatory("pgp_signature")
        return config

class Xen(Source):
    pass

class Kernel(Source):
    """
    The Kernel class handle kernel sources configuration. Regarding the
    other sources, kernel sources require additional parameters, suchs as the
    type of the kernel, which is deduced from the name of its source
    configuration file, as well as its suffix, that is used to produce guests.
    """
    def __init__(self, in_file, suffix=""):
        super().__init__(in_file)
        self.type = None
        self.suffix = suffix

    def _known_types(self):
        """
        We only support Linux and Xen as kernel for now. Others may flawlessly
        work fine, but they have not be tested.
        """
        return ['linux', 'xen']

    def load(self):
        super().load()
        config_name = os.path.basename(self._config_file)
        self.type = config_name.split('-')[0]

        if self.type not in self._known_types():
            raise E.InvalidKernelType(self._config_file,
                                      self.type,
                                      self._known_types())

class Uboot(Source):
    pass

class Toolchain(Source):
    def __init__(self, config_file):
        super().__init__(config_file)
        self.prefix = None
        self.arch = None

    def load(self):
        config = super().load()
        self.prefix = self.get_mandatory(config, "prefix")
        self.arch = self.get_mandatory(config, "arch")
        self.xen_arch = self.get_mandatory(config, "xen_arch")
        # Auto-detect the HOST (in the autotools terminology) The host is the
        # cross-compilation target. It shall not end with a dash (that is
        # brought by the prefix
        self.host = os.path.basename(self.prefix)
        if self.host.endswith('-'):
            self.host = self.host[:-1]
        return config

class Database(collections.MutableMapping):
    """
    The Database class holds the SBXG configuration. It is an aggregation of
    data models and can be accessed in the same fashion than a dictionary.
    This allows this class to be passed directly to the jinja templating engine
    flawlessly.
    """
    def __init__(self, top_source_dir, top_build_dir):
        self.top_source_dir = top_source_dir
        self.top_build_dir = top_build_dir
        self.board = None
        self.genimage = None
        self.kernel = None
        self.uboot = None
        self.toolchain = None

    def use_genimage(self):
        self.genimage = {
            'path': os.path.join(self.top_build_dir, 'genimage_sources'),
            'build_dir': os.path.join(self.top_build_dir, 'build_genimage'),
            'output_path': os.path.join(self.top_build_dir, 'images'),
            'input_path': os.path.join(self.top_build_dir, 'genimage-input'),
            'root_path': os.path.join(self.top_build_dir, '.genimage-root'),
            'tmp_path': os.path.join(self.top_build_dir, '.genimage-tmp'),
            'config': os.path.join(self.top_build_dir, 'genimage.cfg'),
        }

    def set_kernel(self, kernel, kernel_config):
        self.kernel = kernel
        self.kernel.config = kernel_config

    def set_uboot(self, uboot, uboot_config):
        self.uboot = uboot
        self.uboot.config = uboot_config

    def set_toolchain(self, toolchain):
        self.toolchain = toolchain

    def set_xen(self, xen, xen_config):
        self.xen = xen
        self.xen.config = xen_config
        self.xen.host = os.path.basename(self.toolchain.prefix)

    def set_board(self, board):
        self.board = board
        self.set_toolchain(board.toolchain)
        self.use_genimage()
        self.set_kernel(board.kernel, board.kernel_config)
        self.set_uboot(board.uboot, board.uboot_config)
        if board.xen:
            self.set_xen(board.xen, board.xen_config)
        self.guests = board.xen_guests

    def __getitem__(self, attr):
        return getattr(self, attr)

    def __setitem__(self, key, value):
        pass # Immutable, do nothing
    def __delitem__(self, key):
        pass # Immutable, do nothing

    def __len__(self):
        return len(vars(self))

    def __iter__(self):
        for item in vars(self).keys():
            yield item


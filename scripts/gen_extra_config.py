#! /usr/bin/env python3
#
# Copyright (c) 2016, Jean Guyomarc'h <jean@guyomarch.bzh>
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


"""

This script generates Kconfig files by looking at the contents
of a git repository which is supposed to contain repo manifests.

"""

import sys
import argparse
import shutil
import os
import random
import distutils.spawn
import tempfile
import subprocess
import xml.etree.ElementTree as ET

def git_clone(url, path, shallow=True, revision=None):
    args = ["git",  "clone"]
    if shallow:
        args += ["--depth", "1"]
    args += [url, path]
    subprocess.check_call(args)

    if revision is not None:
        subprocess.check_call(["git", "-C", path, "checkout", revision])

def parse_options(argv):
    """
        Simple getopt

        :param argv: Arguments from the command-line
        :returns: object containing the parsed arguments
    """

    parser = argparse.ArgumentParser(description='Openconf generator')
    parser.add_argument('--manifests-revision', type=str)
    parser.add_argument('manifests_url', type=str)
    parser.add_argument('manifests_config', type=str)
    parser.add_argument('kernel_config', type=str)
    return parser.parse_args(argv[1:])

def canonicalize_config(name):
    """
        Converts to uppercases and all non-alphanumeric characters
        into underscores '_'.

        :param name: The name to canonicalize
        :returns: the canonicalized name
    """

    canon = ""
    for char in name:
        char = char.upper()
        if not char.isalnum():
            char = '_'
        canon += char
    return canon

def board_config_get(board):
    """
        Gets the name of a configuration parameter
        for a given board

        :param board: the board's name
        :returns: the configuration name
    """

    return "BOARD_{0}".format(canonicalize_config(board))

def manifest_config_get(board, xml):
    """
        Gets the name of a configuration parameter
        for a given board and manifest

        :param board: the board's name
        :param xml: the board's manifest
        :returns: the configuration name
    """

    return "BOARD_{0}_MANIFEST_{1}".format(canonicalize_config(board),
                                           canonicalize_config(xml))

def defconfig_config_gen(board, defconfig):
    """
        Generates the name of a configuration parameter
        for a given board and defconfig.
        It is randomized because the same config name can
        exist for multiple manifests

        :param board: the board's name
        :param defconfig: the defconfig name
        :returns: the configuration name
    """
    return "BOARD_{0}_DEFCONFIG_{1}_{2}{3}".format(canonicalize_config(board),
                                                   canonicalize_config(defconfig),
                                                   random.randint(0, 99999999),
                                                   random.randint(0, 99999999))

def write_manifests_menuconfig(output_file, manifests):
    """
        Writes a Kconfig file that allows selection of boards
        and manifests.
        This function is in charge to provide a CONFIG_BOARD="Board"
        and CONFIG_MANIFEST="Manifest" using the Kconfig capabilities

        :param output_file: Kconfig to be generated
        :param manifests: Dictionnary: keys are the boards, values
                          are lists of manifests files
    """

    with open(output_file, 'w') as filp:
        conf_boards = []    # List of tuples (board,config)
        conf_manifests = [] # List of tuples (manifest,config)

        #==
        # Prompts for the type of board
        #==
        filp.write("choice\n"
                   "    prompt \"Board Type\"\n"
                   "    help\n"
                   "        Board Family\n\n")
        for board, _ in sorted(manifests.items()):
            config = board_config_get(board)

            filp.write("    config {0}\n"
                       "        bool \"{1}\"\n"
                       .format(config, board))
            conf_boards.append((board, config))
        filp.write("endchoice\n\n")
        #==

        #==
        # Prompts for the manifest (function of the board)
        #==
        for board, files in sorted(manifests.items()):
            board_config = board_config_get(board)
            filp.write("if {0}\n"
                       "    choice\n"
                       "        prompt \"Manifest Selection\"\n"
                       "        help\n"
                       "            Manifest Selection\n\n"
                       .format(board_config))

            for xml in sorted(files):
                config = manifest_config_get(board, xml)
                filp.write("        config {0}\n"
                           "            bool \"{1}\"\n"
                           .format(config, xml))
                conf_manifests.append((xml, config))
            filp.write("    endchoice\n"
                       "endif # {0}\n\n"
                       .format(board_config))
        #==

        #==
        # Auto-select CONFIG_BOARD
        #==
        filp.write("\n\n"
                   "config BOARD\n"
                   "    string\n")
        for board, config in conf_boards:
            filp.write("    default \"{0}\" if {1}\n"
                       .format(board, config))
        #==

        #==
        # Auto-select CONFIG_MANIFEST
        #==
        filp.write("\n\n"
                   "config MANIFEST\n"
                   "    string\n")
        for manifest, config in conf_manifests:
            filp.write("    default \"{0}\" if {1}\n"
                       .format(manifest, config))
        #==

def write_kconfigs_menuconfig(output_file, kconfigs):
    """
        Writes a Kconfig file that allows selection of kernel configurations.
        This function is in charge to provide a CONFIG_BOARD="Board"
        and CONFIG_MANIFEST="Manifest" using the Kconfig capabilities

        :param output_file: Kconfig to be generated
        :param manifests: Dictionnary: keys are the boards, values are
                          dictionnaries where keys are the  and values
                          the list of kernel configurations
    """
    database = {}
    with open(output_file, 'w') as filp:
        filp.write("if USE_BUILTIN_CONFIG\n")
        for board, dic in kconfigs.items():
            board_cfg = board_config_get(board)
            filp.write("if {0}\n".format(board_cfg))
            for man, configs in dic.items():
                man_cfg = manifest_config_get(board, man)
                filp.write("    if {0}\n"
                           "        choice\n"
                           "            prompt \"Kernel Configuration Selection\"\n"
                           "            help\n"
                           "                Selection of the Kernel configuration\n"
                           "\n"
                           .format(man_cfg))
                for config in configs:
                    cfg_param = defconfig_config_gen(board, config)
                    filp.write("            config {0}\n"
                               "                bool \"{1}\"\n"
                               .format(cfg_param, config))
                    database[cfg_param] = (board, config)

                filp.write("        endchoice\n"
                           "    endif # {0}\n".format(man_cfg))
            filp.write("endif # {0}\n".format(board_cfg))

        filp.write("\n\n"
                   "config DEFCONFIG\n"
                   "    string\n")
        for cfg_param, pair in database.items():
            filp.write("    default \"{0}/{1}\" if {2}\n"
                       .format(pair[0], pair[1], cfg_param))
        filp.write("endif\n")


def manifests_lookup(directory):
    """
        Extracts a dictionary where the keys are the boards
        and the values are lists of manifests files.

        :param directory: the directory to walk
        :returns: The dictionary described earlier.
    """

    manifests = {}
    top_dir = True
    for dirpath, _, filenames in os.walk(directory):
        if top_dir is True: # Skip files in top directory
            top_dir = False
            continue
        if ".git" in dirpath: # Skip .git/ directory
            continue

        # Board name is the name of the directory
        board = os.path.basename(dirpath)

        # Search all the manifests (.xml files)
        fileslist = []
        for filename in filenames:
            if os.path.splitext(filename)[1] == ".xml":
                fileslist.append(filename)
        if len(fileslist) < 1: # No manifests in directory, skip it
            continue

        manifests[board] = fileslist
    return manifests


def kconfigs_lookup(directory, manifests):
    """
        Extracts a dictionary where the keys are the manifests
        and the values a dictionary where the keys are the boards
        and the values are a list of kernel configurations.

        :param manifests: a dictionary of manifests for each board configuration
                          as returned by the manifests_lookup() function
        :returns: The dictionary described in the preamble
    """

    kconfigs = {}
    clones_cache = {}

    for board, manifs in manifests.items():
        kconfigs[board] = {}
        for man in manifs:
            # Path of the manifest file
            path = "{0}/{1}/{2}".format(directory, board, man)

            # Iterate over the XML of the manifest to find out the
            # remote and where to fetch it
            tree = ET.parse(path)
            root = tree.getroot()
            remotes = root.findall('remote')
            for child in root:
                if child.tag == "project" and child.attrib["path"] == "kernel-configs":
                    name = child.attrib["name"]
                    remote = child.attrib["remote"]
                    revision = child.attrib["revision"]
                    remote_url = None
                    for rem in remotes:
                        if rem.attrib["name"] == remote:
                            remote_url = rem.attrib["fetch"]
                            break
                    if remote_url is None:
                        raise RuntimeError("Failed to find remote")
                    break

            # Remote is found, this is what we must clone
            clone_url = "{0}/{1}".format(remote_url, name)

            # Cloning takes a loooot of time. If there are duplicated
            # URLs to be cloned (there will!!), clone them only once.
            cache_entry = (clone_url, revision)
            if not cache_entry in clones_cache:
                tmpdir = tempfile.mkdtemp()
                try:
                    git_clone(clone_url, tmpdir, False, revision)
                except subprocess.CalledProcessError:
                    clones_cache[cache_entry] = None
                else:
                    clones_cache[cache_entry] = tmpdir

            # In the kernel configs directory get for the current board
            tmpdir = clones_cache[cache_entry]

            if tmpdir is not None:
                for d in os.listdir(tmpdir):
                    if board == d:
                        configs = os.listdir("{0}/{1}".format(tmpdir, d))
                        kconfigs[board][man] = configs
                        break

    # Remove all temporary directories after all clones are done
    for _, tmpdir in clones_cache.items():
        if tmpdir is not None:
            shutil.rmtree(tmpdir)

    print(kconfigs)

    return kconfigs


def main(argv):
    """
        Main routines

        :params argv: arguments from the command-line
        :returns: the exit code of the main()
    """

    ret = 0 # Return status

    try:
        parser = parse_options(argv)

        # Determine in which folder should the manifests be retrieved
        lookup_dir = tempfile.mkdtemp()

        # Collect the manifests from their git repository
        if parser.manifests_revision:
            git_clone(parser.manifests_url, lookup_dir, False,
                      parser.manifests_revision)
        else:
            git_clone(parser.manifests_url, lookup_dir)

        manifests = manifests_lookup(lookup_dir)
        kconfigs = kconfigs_lookup(lookup_dir, manifests)

        # Remove generated directory when none was specified
        shutil.rmtree(lookup_dir)

        write_manifests_menuconfig(parser.manifests_config, manifests)
        write_kconfigs_menuconfig(parser.kernel_config, kconfigs)

    except RuntimeError as exc:
        print("*** {0}".format(exc), file=sys.stderr)
        ret = -1

    return ret

if __name__ == "__main__":
    sys.exit(main(sys.argv))

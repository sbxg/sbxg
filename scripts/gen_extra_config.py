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
import distutils.spawn
import tempfile
import subprocess

def parse_options(argv):
    """
        Simple getopt

        :param argv: Arguments from the command-line
        :returns: object containing the parsed arguments
    """

    parser = argparse.ArgumentParser(description='Openconf generator')
    parser.add_argument('--fetch-dir', type=str)
    parser.add_argument('url', type=str)
    parser.add_argument('openconf', type=str)
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
        Generates the name of a configuration parameter
        for a given board

        :param board: the board's name
        :returns: the configuration name
    """

    return "BOARD_{0}".format(canonicalize_config(board))

def manifest_config_get(board, xml):
    """
        Generates the name of a configuration parameter
        for a given board and manifest

        :param board: the board's name
        :param xml: the board's manifest
        :returns: the configuration name
    """

    return "BOARD_{0}_MANIFEST_{1}".format(canonicalize_config(board),
                                           canonicalize_config(xml))

def write_menuconfig(output_file, manifests):
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
        if parser.fetch_dir is None:
            lookup_dir = tempfile.mkdtemp()
        else:
            lookup_dir = parser.fetch_dir

        # Collect the manifests from their git repository
        git = distutils.spawn.find_executable("git")
        subprocess.check_call(
            [git, "clone", "--depth", "1", parser.url, lookup_dir]
        )
        manifests = manifests_lookup(lookup_dir)

        # Remove generated directory when none was specified
        if parser.fetch_dir is None:
            shutil.rmtree(lookup_dir)

        write_menuconfig(parser.openconf, manifests)

    except RuntimeError as exc:
        print("*** {0}".format(exc), file=sys.stderr)
        ret = 1

    return ret

if __name__ == "__main__":
    sys.exit(main(sys.argv))

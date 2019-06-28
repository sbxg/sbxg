# Copyright (c) 2019 Jean Guyomarc'h
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

import os
from pathlib import Path

def _walk_files(lib_dirs, directory):
    for lib_dir in lib_dirs:
        for root, _, files in os.walk(lib_dir / directory):
            for item in files:
                yield item, Path(root).name, str(Path(root, item))

def _walk_yaml_files(lib_dirs, directory):
    for item, item_dir, item_path in _walk_files(lib_dirs, directory):
        if item_path.endswith('.yml'):
            name = os.path.splitext(item)[0]
            yield name, item_dir, item_path

def get(lib_dirs):
    """
    Collect the contents of the SBXG library and store them in a well-defined
    data structure.

    Args:
        lib_dirs (list): List of directories that consistute the SBXG library
    """
    sources = []
    toolchains = []
    configurations = []
    boards = []
    images = []
    bootscripts = []

    # Search the sources (files that describe how to get components)
    for item, item_dir, item_path in _walk_yaml_files(lib_dirs, "sources"):
        sources.append({
            "type": item_dir,
            "name": item,
            "path": item_path,
        })

    # Search for toolchain descriptions
    for item, _, item_path in _walk_yaml_files(lib_dirs, "toolchains"):
        toolchains.append({
            "name": item,
            "path": item_path,
        })

    # Search for components descriptions
    for item, item_dir, item_path in _walk_files(lib_dirs, "configs"):
        configurations.append({
            "type": item_dir,
            "name": item,
            "path": item_path,
        })

    # Search the boards
    for item, _, item_path in _walk_yaml_files(lib_dirs, "boards"):
        boards.append({
            "name": item,
            "path": item_path,
        })

    # Search the bootscripts
    for item, _, item_path in _walk_files(lib_dirs, "bootscripts"):
        bootscripts.append({
            "name": item,
            "path": item_path,
        })

    # Search the images
    for item, _, item_path in _walk_files(lib_dirs, "images"):
        images.append({
            "name": item,
            "path": item_path,
        })

    return {
        "sources": sources,
        "toolchains": toolchains,
        "configurations": configurations,
        "boards": boards,
        "bootscripts": bootscripts,
        "images": images,
    }

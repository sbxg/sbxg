#! /usr/bin/env python
#
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

import argparse
import os
import sys

import jsonschema
import yaml

def getopts(argv):
    parser = argparse.ArgumentParser(description='Model Checker')
    parser.add_argument(
        'type', type=str, choices=['toolchain', 'kernel', 'uboot', 'board'],
        help='Type of the config to be checked'
    )
    parser.add_argument(
        'config', type=str,
        help='Path to the configuration to be checked'
    )
    return parser.parse_args(argv[1:])

def main(argv):
    args = getopts(argv)

    scripts_dir = os.path.dirname(os.path.realpath(__file__))
    schema = os.path.join(scripts_dir, 'schema', args.type + '.yml')

    with open(schema, 'r') as stream:
        schema_data = yaml.load(stream.read())

    with open(args.config, 'r') as stream:
        config_data = yaml.load(stream.read())

    jsonschema.validate(config_data, schema_data)

if __name__ == '__main__':
    main(sys.argv)

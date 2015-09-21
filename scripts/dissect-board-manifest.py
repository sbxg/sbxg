#!/usr/bin/env python2.7
#
# Copyright (c) 2015, Jean Guyomarc'h <jean.guyomarch@gmail.com>
#


import sys
import os.path



def parse_manifest_filename(filename):
    board, sep, manifest = filename.partition('/')
    args = manifest.split('-')
    if len(args) < 3:
	sys.stderr.write("*** Invalid filename\n")
	return []
    return board, args[0], args[1], args[2:]

def manifest_data_write(output, board, kernel, kernel_version, args):
    # Set the KERNEL_CONFIG
    buf = 'KERNEL_CONFIG="kernel-configs/{}/{}'.format(board, kernel_version)
    for arg in sorted(args):
	buf += '-{}'.format(arg)
    buf += '"\n'

    # Tell the boad name
    buf += 'BOARD_NAME="{}"\n'.format(board)

    # Tell the config to source the board config
    buf += 'BOARD_CONFIG="./boards/${BOARD_NAME}.conf"\n'
    buf += '. "${BOARD_CONFIG}"\n'

    # Save in a file...
    file = open(output, 'w')
    file.write(buf)
    file.close()


def main():
    # Check that one argument exactly is provided
    if len(sys.argv) != 2:
	sys.stderr.write("*** Need one argument: the board manifest\n")
	return 1
    else:
	# Remove the extension of the file
	filename, ext = os.path.splitext(sys.argv[1])

	# Tokenize the manifest filename
	board, ker, ker_version, args = parse_manifest_filename(filename)

	# Create a configuration file from the manifest
	manifest_data_write('config.manifest', board, ker, ker_version, args)
    return 0


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)


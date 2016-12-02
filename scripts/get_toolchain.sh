#! /usr/bin/env sh
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

set -e
set -u

die() {
   echo "*** $@" 1>&2
   exit 1
}

if [ $# -ne 3 ]; then
   die "Usage: $0 URL DESTDIR NAME"
fi

# URL: where to get the toolchain
# DESTDIR: in which directory it must be stored
# NAME: the name of the extracted directory
URL="$1"
DESTDIR="$2"
NAME="$3"

if [ -d "$DESTDIR/$NAME" ]; then
   echo "\"$DESTDIR/$NAME\" already exists."
   exit 0 # This is not a failure!
fi

mkdir -p "$DESTDIR"
cd "$DESTDIR"
TMPFILE="$(mktemp "dl.XXXXXXXXX.tmp")"

clean() {
   rm "$TMPFILE"
}
trap clean EXIT

echo "Downloading $URL. This may take a while..."
wget --quiet "$URL" -O "$TMPFILE"
tar -xf "$TMPFILE"

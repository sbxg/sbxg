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

#
# Hooker is a shell wrapper that logs every action taken by make in a
# specific log file.
#

set -e

if [ -z "$MAKE_SHELL" ]; then
   MAKE_SHELL=/bin/sh
fi

set -u

# Log file will be in the current working directory
LOG_FILE=sbxg.log

# Log the command
echo "[$(date "+%Y-%m-%d.%H:%M:%S")] $MAKE_SHELL $@" >> "$LOG_FILE"

# Execute the actual shell command - don't quote the $MAKE_SHEL.
exec $MAKE_SHELL "$@"

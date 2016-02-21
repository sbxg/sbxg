#! /usr/bin/env sh
#
# Copyright (c) 2016 Jean Guyomarc'h <jean.guyomarch@gmail.com>
#
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
# along with SBXG  If not, see <http://www.gnu.org/licenses/>.


CWD="$(dirname "$0")" # Where the script resides

# Returns the git version as an integer
git_version_get() {
   echo "$(git --version | grep -o "[0-9]\.[0-9]\.[0-9]" | sed 's/\.//g')"
}

git_remote_get() {
   # FIXME origin is assumed to be the remote
   echo "origin"
}

git_dir="$CWD/../.git"
if [ -d "$git_dir" ]; then
   git_version="$(git_version_get)"
   remote="$(git_remote_get)"

   # Git 2.7.0 provides git remote get-url. Previous versions don't...
   if [ "$git_version" -ge 270 ]; then
      url="$(git --git-dir "$git_dir" remote get-url "$remote")"
   else # < git 2.7.0
      url="$(git remote -v | grep "${remote}.*(fetch)$" | cut -d ' ' -f 1 | cut -f 2)"
   fi
   base_url="$(dirname "$url")"
   echo "$base_url"
else
   exit 1
fi

# Copyright (c) 2016, Jean Guyomarc'h <jean.guyomarch@gmail.com>
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

# Extract the git hash (short version) from a git repository specified
# as $(1)
define git-hash-get
$(shell \
   git_dir="$(1)/.git"; \
   if [ -d "$$git_dir" ]; then \
      git --git-dir "$$git_dir" rev-parse --short HEAD; \
   fi
)
endef

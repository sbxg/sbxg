#!/bin/sh

set -e

CONFIG_MAKEFILE=./makefile.vars
CONFIG_USER=./config.user
CONFIG_TEMPLATE=./config.template
CONFIG_MANIFEST=./config.manifest

# If config.user is not created, create one from the template
if [ ! -f "$CONFIG_USER" ]; then
   # No template file available: something very wrong occured
   if [ ! -f "$CONFIG_TEMPLATE" ]; then
      echo "*** \"$CONFIG_TEMPLATE\" does not exist. Unable to generate \"$CONFIG_USER\"" 1>&2
      exit 1
   fi
   cp "$CONFIG_TEMPLATE" "$CONFIG_USER"
fi

# Source the user config
. "$CONFIG_USER"

# Get the *names *of all the variables in the config
# From config.user:
#  - remove all comments
#  - keep only variables
#  - format them nicely (no duplicates, no empty lines)
LIST="$(sed -e 's/\#.*$//g' "$CONFIG_USER" "$CONFIG_MANIFEST" "$BOARD_CONFIG" \
   | grep -o  "[a-zA-Z0-9_]*=" | cut -d '=' -f 1 | sort | uniq | tr  "\n" " ")"


# Create an empty file
cat > "$CONFIG_MAKEFILE" << EOF
# $CONFIG_MAKEFILE
# File auto-generated by $0.
# ==== DO NOT EDIT BY HAND =====

EOF

# Write in the makefile.vars the variables in Make's syntax
for l in $LIST; do
   exp="$(eval echo \$$l)"
   echo "$l := $(eval echo -n $exp)" >> "$CONFIG_MAKEFILE"
done


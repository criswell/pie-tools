#!/usr/bin/env bash

# Sets up a virtual environment for Nikola in as Python angostic as
# possible

PYVENV=yes
VIRTENV=yes

# Figure out what we have
pyvenv -h >/dev/null 2>&1 || unset PYVENV
virtualenv --version >/dev/null 2>&1 || unset VIRTENV

if [ -n "$PYVENV" ]; then
    echo "pyvenv found, using that..."
elif [ -n "$VIRTENV" ]; then
    echo "virtualenv found, using that..."
else
    echo "no suitable python virtual env tool found, aborting"
fi

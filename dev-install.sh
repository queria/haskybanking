#!/bin/bash
# vim: set et sw=4 ts=4:

set -o errexit

cd $(dirname $0)
if [[ ! -d .venv ]]; then
    virtualenv --system-site-packages .venv
fi
. .venv/bin/activate
pip install -r requirements.txt
pip install -r dev-requirements.txt


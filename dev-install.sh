#!/bin/bash
# vim: set et sw=4 ts=4:

set -o errexit


cd $(dirname $0)

./install.sh

. .venv/bin/activate
pip install -r dev-requirements.txt


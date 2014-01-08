#!/bin/bash
# vim: set et sw=4 ts=4:

set -o errexit

cd $(dirname $0)

if [[ ! -d .venv ]]; then
    virtualenv --no-site-packages .venv
fi

. .venv/bin/activate
if [[ -z "$VIRTUAL_ENV" || "$(which pip)" == "/usr/bin/pip" ]]; then
    echo "VirtualEnv activation failed?!"
fi
pip install -r requirements.txt

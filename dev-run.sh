#!/bin/bash
# vim: set et sw=4 ts=4:

cd $(dirname $0)
[[ -z "$VIRTUAL_ENV" && -d .venv ]] && . .venv/bin/activate
if uwsgi --help|grep -q python-autoreload; then
    uwsgi -T -p 4 --reload-on-exception 1 --python-autoreload 1 --http :5000 --wsgi-file haskybanking/app.py
else
    uwsgi -T -p 4 --reload-on-exception 1 --http :5000 --wsgi-file haskybanking/app.py
fi

#pwd
#export PYTHONPATH="$PYTHONPATH:$(readlink -f .)"
#echo $PYTHONPATH
#python haskybanking/app.py

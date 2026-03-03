#!/usr/bin/env sh
# note: only run on PythonAnywhere while in venv (`workon`)

# update venv
pip install -r requirements.txt

# create production-ready .env
python scripts/env.py
sed -i '1iPROD=""' .env

# run migrations
python manage.py migrate
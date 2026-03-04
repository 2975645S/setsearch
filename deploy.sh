#!/usr/bin/env sh
# note: only run on PythonAnywhere while in venv (`workon`)

pip install -r requirements.txt

python scripts/env.py
sed -i '1iPROD=""' .env

python manage.py migrate
python manage.py collectstatic
#!/usr/bin/env sh

# reset venv
rm -rf .venv
python -m venv .venv
pip install .

# create production-ready .env
python env.py
sed -i '1iPROD=""' .env
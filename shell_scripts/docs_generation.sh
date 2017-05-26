#!/bin/bash
cd "$1"
virtualenv -p python3 .venv
source .venv/bin/activate
pip3 install -r requirements.txt
pip3 install sphinx
cd docs/
make html

#!/bin/bash
cd "$1"
virtualenv -p python3 .venv
source .venv/bin/activate
pip3 install -r requirements.txt
pip3 install pylint
cd "$2"
find . -iname "*.py" |xargs pylint --output-format=json > pylint_results.json

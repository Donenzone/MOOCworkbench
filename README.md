![build](https://travis-ci.org/jlmdegoede/MOOCworkbench.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/jlmdegoede/MOOCworkbench/badge.svg?branch=master)](https://coveralls.io/github/jlmdegoede/MOOCworkbench?branch=master)
[![Code Health](https://landscape.io/github/jlmdegoede/MOOCworkbench/master/landscape.svg?style=flat)](https://landscape.io/github/jlmdegoede/MOOCworkbench/master)

# MOOC workbench
A workbench for MOOC research, written in Django, meant to improve the reproducibility of experiments.


## Setting up
In order to run this development version locally, make sure the following dependencies are met:
- Python 3.6 and redis-server are required
- Install pip3 and virtualenv if you haven't already: `sudo apt-get install python3-pip python3-dev virtualenv`
- Set up a virtuelenv: `virtualenv -p python3 moocv`
- Activate the virtualenv: `source moocv/bin/activate`
- Install the MOOC workbench requirements: `pip3 install -r requirements.txt`
- Migrate the database: `python3 manage.py migrate`
- Create the first super user: `python3 manage.py createsuperuser`
- Load data from the fixtures: `python3 manage.py loaddata steps.json`
- Start the Redis server: `redis-server &`
- Run the local version of the MOOC workbench: `python3 manage.py runserver`
- For some functionality, Celery is required, so start Celery in a seperate tab with: `celery -A MOOCworkbench worker -l info`

After running the version, in order to use the social functions, you need to go to /admin and add a Social application. At least create a social app for GitHub and enter your Client ID en Client Secret key for the MOOC workbench to be able to use GitHub functionality.

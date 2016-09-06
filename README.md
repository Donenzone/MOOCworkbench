![build](https://travis-ci.com/Donenzone/MOOCworkbench.svg?token=F5iwxJRyXWzaM4JVyZqS&branch=master)

# MOOC workbench
A workbench for MOOC research, written in Django


## Setting up
In order to run this development version locally, make sure the following requirements are met:
- Right now, the workbench is only tested on OS X 10.11 and Ubuntu 16.04
- Python 3.5, Redis server and Git are required
- Install pip3 if you haven't already: `sudo apt-get install python3-pip python3-dev build-essential`
- Upgrade pip to the latest version: `sudo pip install --upgrade pip`

Check out the source code, open a terminal and cd into the source code dir.
Set up a virtuelenv or install the dependencies globally:
- `pip3 install -r requirements.txt`
- Migrate the database: `python3 manage.py migrate`
- Start the Redis server: `redis-server &`
- Run the local version of the MOOC workbench: `python3 manage.py runserver`

==========
Deployment
==========

Before you begin, first go to the folder MOOCworkbench/ and edit the file production_settings.py_template with the relevant data. You can set the WEBHOOK_SECRET_KEY as a random string, make sure that ALLOWED_HOSTS contains your FQDN and enter a SECRET_KEY. Make sure to keep this information secure. For the Forgotten password functionality, a valid SMTP server is required, so enter this data now. Finally, for REDIS_HOST, if you deploy with Docker, set this value to 'redis', else to 'localhost' or wherever your own Redis server is reachable.

Docker
------
To deploy the MOOC workbench and use it in production, Docker is recommended, but not required.
After you have installed Docker on the relevant platform, run the following commands::

  docker-compose build
  docker-compose up -d

Then, jump into a bash session in the web Docker container to run some set-up commands::

  docker exec -t -i moocworkbench_web_1 bash
  cd /workbench
  ./setup.sh
  exit

You can now visit http://localhost:8000 in a browser to see the workbench and sign in with the automatically created administrator account.

Flower & PyPi server
~~~~~~~~~~~~~~~~~~~~
On http://localhost:5555 Flower is hosted, which can be used to track long-running Celery tasks and stop failed tasks.

The packages present in the PyPi server can be viewed on http://localhost:8001.

Make sure that your cookiecutter templates in requirements.txt, for a Python template, point to your own PyPi server (the ---extra-index-url switch at the top of the file), else custom packages cannot be installed by the users.

Reverse proxy
~~~~~~~~~~~~~
It is recommended to host all these services with a reverse proxy in your favourite webserver, for example nginx. An example configuration can be found here.

Without Docker
--------------
If you prefer to run the workbench without Docker, make sure the system you are deploying on meets the following requirements:

- Python 3.5/3.6
- Redis server

Then, to deploy the workbench:

- (Create a virtual environment)
- Install the dependencies in this virtualenv with pip3 install -r requirements.txt
- Run ./setup.sh to migrate the database, collect the static files, create an admin user and load initial data

Start the webserver with workers and Celery workers

* daphne -p 8000 MOOCworkbench.asgi:channel_layer
* python3 manage.py runworker
* celery -A MOOCworkbench worker -l info
* celery flower -A MOOCworkbench --address=0.0.0.0 --port=5555
* pypi-server -p 8001 packages/

Preferably run these commands in for example supervisor.
==========
Deployment
==========

Docker
------
To deploy the MOOC workbench and use it in production, Docker is recommended, but not required. After you have installed Docker on the relevant platform, run the following commands::

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
If you prefer to run the workbench without Docker, make sure the system you are deploying on meets the following requirements.
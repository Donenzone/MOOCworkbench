[![Build Status](https://travis-ci.org/jlmdegoede/MOOCworkbench.svg?branch=master)](https://travis-ci.org/jlmdegoede/MOOCworkbench)
[![Coverage Status](https://coveralls.io/repos/github/jlmdegoede/MOOCworkbench/badge.svg?branch=master)](https://coveralls.io/github/jlmdegoede/MOOCworkbench?branch=master)
[![Requirements Status](https://requires.io/github/jlmdegoede/MOOCworkbench/requirements.svg?branch=master)](https://requires.io/github/jlmdegoede/MOOCworkbench/requirements/?branch=master)

# MOOC workbench
A workbench that helps to improve the reproducibility and quality of MOOC experiments. This is a Web application that allows for the creation of experiments, and that provides services for your experiments, such as cookiecutter templates meant for data science, automatic configuration of static code analysis, continuous integration, testing and documentation generation.

It also allows for easier sharing of code. With a click of the button, you can create ready-to-install packages of the code that you have written in an experiment and want to share with others. It does require some manual labor of course, namely ensuring that you export the neccessary functions, but it vastly simplifies this process.

The MOOC Workbench also serves as an information sharing platform for researchers, where they can share valuable information and resources regarding useful software tools and packages.

## Setting up
In order to run and deploy this version, follow these steps:
- Python 3.6 and Redis are required
- Install the requirements, preferably in a vritualenv: `pip3 install -r requirements.txt`
- Migrate the database: `python3 manage.py migrate`
- Create the first super user: `python3 manage.py createautoadmin`
- Load data from the fixtures: `python3 manage.py loaddata fixtures/*.json`
- Run the local version of the MOOC workbench: `python3 manage.py runserver`
- For a lot of functionality, Celery is required, so start this with: `celery -A MOOCworkbench worker -l info`

After running the version, in order to use the social functions, you need to go to /admin and add a Social application. At least create a social app for GitHub and enter your Client ID en Client Secret key for the MOOC workbench to be able to use GitHub functionality.

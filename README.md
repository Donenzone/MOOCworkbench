[![Build Status](https://travis-ci.org/MOOCworkbench/MOOCworkbench.svg?branch=master)](https://travis-ci.org/MOOCworkbench/MOOCworkbench)
[![Coverage Status](https://coveralls.io/repos/github/MOOCworkbench/MOOCworkbench/badge.svg?branch=master)](https://coveralls.io/github/MOOCworkbench/MOOCworkbench?branch=master)
[![Requirements Status](https://requires.io/github/MOOCworkbench/MOOCworkbench/requirements.svg?branch=master)](https://requires.io/github/MOOCworkbench/MOOCworkbench/requirements/?branch=master)

# MOOC workbench
This workbench helps to improve the reproducibility and quality of MOOC experiments. It is a web application that allows for the creation of experiments and that provides services for your experiments to improve reproducibility. For example, the workbench provides cookiecutter templates to initialize and kickstart your experiments with, and provides useful services such as Travis and Coveralls integration, documentation generation and static code analysis. It also helps you define your dependencies in easy to use front-end and helps creating a data schema using JsonTableSchema. All these things together help so that your MOOC experiment is reproducible by others.

The workbench also allows for easier sharing of code with other researchers. With a click of the button, you can create ready-to-install packages of the code that you have written in an experiment and want to share with others. It does require some manual labor of course, namely ensuring that you export the neccessary functions, but it vastly simplifies this process.
The MOOC Workbench also serves as an information sharing platform for researchers. They can share valuable information and resources regarding useful software tools and packages.

Right now, the workbench only supports Python and R in beta, as the R functionality has not been tested as well as the Python functionality. 

## Documentation
The documentation is published on [GitHub Pages](https://moocworkbench.github.io/MOOCworkbench).

## Deployment
To deploy the workbench, we recommend the use of Docker. Download a ZIP file from the [Release page](https://github.com/MOOCworkbench/MOOCworkbench/releases), run docker-compose and docker up -d to start the containers. You can also deploy without Docker, see the [Deploy instructions](https://moocworkbench.github.io/MOOCworkbench/deployment.html) in the documentation for more information.

After running the workbench, in order to use the social functions, you need to go to the admin section and add a Social application. Ccreate a social app for GitHub and enter your Client ID en Client Secret key for the workbench.

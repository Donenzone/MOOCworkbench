========
Features
========

The workbench helps you getting started with your experiment and applies software engineering principles to your data science experiments.
Here are some of the main features of the workbench.

Help you with your experiment
=============================
The main feature of the workbench is to help you with your (data science/MOOC) experiments. The workbench is designed to integrate seamlessly into your workflow.
The workbench does this through various ways.

GitHub integration
==================
The workbench integrates with GitHub to allow for the creation of a new GitHub repository for your experiment or your package.
It also pushes changes you make to GitHub, for example with regards to the data schema and your dependencies, and you can view files from your GitHub repository in the workbench with static code analysis results integrated.

Boilerplate code
================
You can choose which boilerplate code to use with the workbench. These templates are cookiecutter templates, so everyone can create their own.
By default, three cookiecutter templates are present: two for Python and one for R. They contain code to get started with building your experiment, by providing default folders, a Makefile and configurations for several useful services.
The workbench supports both Python 3 and R. For R, we provide boilerplate code with Packrat, so that you can ship your experiment as a all-in-one script.

Continuous integration
======================
Travis CI is useful as it automatically runs all your tests. This means you always have insight in the quality of your experiment, and it is ensured your experiment runs on someone else's computer.

Data schema
===========
Define a data schema: data science experiments often use CSV files that are or cannot be provided, due to containing personal data or licensing issues. The workbench solves this problem by integrating jsontableschema, which creates a data schema of your CSV files used for your experiment. A data schema contains all the fields in your CSV, the constraints, data types and format. This way, when another researchers wants to check your experiment, the immediately know which data they need to gather.

Dependency management
=====================
Helps you manage your experiment dependencies: oftentimes, researchers forget to write down which packages they've used in their experiment, the workbench helps you write these down, which improves the repeatability of your experiment.

Documentation
=============
Documenting your code is easy, making it easily accessible, not so much. The workbench automatically extracts your Python docstrings, uses Sphinx to build the HTML files for them and publishes them on GitHub using gh-pages.

Publication
===========
Once your are done with your experiment, you want to ensure that the paper references the correct source code version. With the workbench, you can publish your experiment afterwards: Simply choose to publish, and the workbench creates a GitHub release with a unique tag that you can use to reference in the paper. Also, we create a read-only version of your experiment page in the workbench, so that you can share the link with everyone and others can see in one glance what you've done.

Share information
=================
The workbench allows you to share useful packages or package resources with other researchers. Found an interesting blog about pandas? Share it! Found a new, useful data science package? Share it! Also, for packages on PyPi, the workbench automatically tracks new versions, so that you are always up-to-date for having the new versions.

Tracks experiment progress
==========================
The workbench tracks your experiment progress. It monitors recent builds, the amount of uncovered documented classes and functions, how often you commit, if you've defined all your dependencies and more. This way, you can always see at a glance which aspect of your experiment needs some more attention!


Conclusion
==========
Overall, the workbench helps data scientists and large-scale learning analytics researchers to write more repeatable and reproducible experiments.
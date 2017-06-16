===============
Getting started
===============

To get started with the workbench, create a user account by clicking *Create an account*. Fill in the required information and sign in with your new account.


Create an experiment
====================
To create your first experiment, click on the right *Create New Experiment*. The first time, you are redirected to the Social applications page, prompting that you are required to sign in with GitHub before continuing. Please do so, by clicking *Connect to GitHub*.
Once you are signed in and connected, go back to the index page and click *Create New Experiment* again. Fill in the required information, namely a descriptive title (this also becomes the title of your GitHub repository) and a description of your project. Finally, choose which boilerplate code template you want to use for this experiment: You can choose between a Python or an R template. Click *Create Experiment and Choose Experiment Steps*.

Now, behind the scenes your experiment is being initialized. It might take some time before the process starts, because first a worker has to be found to process your task. You can browse other pages in the workbench in the meantime and later on return to your experiment. Once your task is completed, you are automatically redirected to the experiment steps page.

Add existing experiment
-----------------------
If you want to add an existing GitHub repository, enter in the title field of the experiment creation form the literal title of your existing GitHub repository. The workbench will recognise a repository already exist and leave it as-is, continuing immediately to the choosing experiment steps page. Make sure to only add a GitHub repository that uses a supported cookiecutter template, else we cannot guarantee all the workbench services working correctly.


Choosing experiment steps
-------------------------
On the experiment steps page, you can choose which steps your experiment will go through. You can choose from the following steps:

- Data: The data step is meant for writing the code for data gathering, data filtering and data cleaning.
- Schema: The schema step is a short interlude step to create a dataschema.
- Features: The feature step is meant to write the code to extract the features from your dataset.
- Modelling: The modelling step is to model the features from your data set.
- Visualization: Finally, the visualization step is meant for writing code to visualize your results.

Each experiment step corresponds with a specific folder or file in the cookiecutter template. For example, the data step in the default Python template is located in */src/data*. When this step is active, the workbench only scans and focuses on the code in that step, by running static code analysis, recommending useful packages in this step and more. After you're done with a step, which means for the data step for example that you've written code to gather, filter and process your data, you can continue to the next step, but not before you can see how you've done in this step, with regards to the amount of code covered with tests and documentation, if you've committed often enough and how your code does for static code analysis. Afterwards, you have the possibility to take the code you have written in the Data step, and create a package from it. This can be done in a few clicks.

Experiment set-up
-----------------
Once you have selected your experiment steps, it is time to set-up your experiment. The workbench now provides detailed instructions on how to clone your GitHub repository and set-up a suitable development environment. Setting up a virtual environment for Python is optional, as some users encountered some problems with the used libraries.

Next, it is recommended to configure Travis by signing in at least once with your Travis account and syncing your repositories. Back in the workbench you can click *Enable now* once you've done that. Do the same for Coveralls to enable that as well with just a few clicks.


Experiment detail page
======================
On the experiment detail page, you can track your experiment progress with the steps you've just selected. For each step, you can view the files in that step.

Dashboard
---------
On the Dashboard, you can see an overview of how you are doing. It can take some time before you see the results. When you see a red or yellow header, your attention is required for that aspect. Green means everythings OK and you're doing fine.

Read Me
-------
On the Read Me page, you can view the readme of your GitHub repository, which is by default provided by your boilerplate code. For the Python data science template, you can view the different folders and what they are meant for.

Dependencies
------------
When you are using an extra package in your experiment, for example pandas or something else, you can add the name of the package and the used package version here. If you prefer, for Python or packrat, to define them in requirements.txt or packrat.lock, you can also do that. On the next commit, the workbench parses either file and updates your dependencies automatically.

Schema
------
On the Schema tab, you can view your created JSON Table Schema once you have arrived at that step, review if everything is correct and make changes if required.

Settings
--------
On the Settings page, you can change some settings, such as the GitHub URL, title and the description of your experiment.

What's next?
============
Now that you're walked through all the main functions of the workbench, it is time to get started. Open the files in the active step and write code to accomplish your data science tasks! Regularly check the Experiment detail page to see how you are doing and make sure to make improvements where necessary.


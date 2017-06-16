=======================
Packages & Code Sharing
=======================

One of the more important features of the workbench is the *Packages* section.

Creating a package from an experiment step
==========================================
The recommended way to create a package, is to create an immediately after you have completed a step of your experiment. That's when you're still familiair with the code and it's easiest to determine if it's useful for a package and you can make some improvements if necessary. To create a package, complete a step by clicking on the experiment detail page on *Complete and go to next*. Review the score card and click *Continue towards next step*. In the modal dialog that appears, choose for *Yes, create a package from the code in this step and publish it on the Marketplace*.

Enter a name for your new package: make sure this is all lowercase, no spaces and only letters. Also enter a description. Choose a category for your package and tell us which programming language your package is for. Click *Create New Package*.

What happens next, is that the workbench automatically extracts the code from your experiment step, but keeps the git history of your commits, which is useful if you ever want to go back or review older code in your package. It then creates the boilerplate code for either Python or an R package. For Python, we create a pip package.

Once your package is created, you are redirected to the Internal package dashboard. From here, you can add dependencies for your packages, view the package readme, create a new version or publish your package.

Preparing for publication
-------------------------
Now that you have created your package, it is not yet published and thus not yet visible for others. Before that, we recommend that you

- check that all the dependencies are present on the Dependencies tab, and if not add them
- write a Getting started guide on how to use your package by going to the *Resources* tab and creating a new package resource. Make sure this Package resource contains which functions/classes your packages exposes, what these do and how they are to be used (e.g. which parameters, what behaviour)
- we recommend to clone your package locally and review the code. Optionally, you can make functions private in Python by starting the function name with an underscore (for example to make make_dataset private, change the name to _make_dataset)
- the source code of your package is placed in the folder <packagename>/
- you can test your pacakage as follows: Open a command-line and *cd* to your package directory. Run the command *python3 setup.py install*. Next, open a Python3 shell and type import <packagename>. You can then call and try out your functions in your package.

Once you have done all that, go to the Internal package dashboard and click *Publish My Package*. Follow the final checklist and click the button to publish your package. It is then visible on the Packages section of the workbench and will be added to the PyPi packages directory, if it is a Python package.

Creating an empty package
=========================
If you want to start from scratch, you can also create an empty package. Go to the *Packages* index page and click *Create New Package* / *Create an Internal Package*.


Installing and using a package in your experiment
=================================================
If you want to use an existing internal package into your own experiment, you can add this package several ways.

On the package detail page, click *Package options* / *Install package*. Choose the experiment into which you want to install this package. The package is added to your dependencies file. Locally, pull in the git changes and update your environment, for Python with the commando *make requirements*.

On the Dependencies tab of your experiment detail page, type the name of the package you want to install. The workbench will autocomplete the name and version of packages present in the workbench. Add this dependency and follow the same steps as previously to install the package locally.

For Python, we add an extra index-url for pip which points to the workbenches custom PyPi server. This way, these local packages can be installed and used in your own Python scripts. The Pypi server is public, so it can be used by other researchers not part of the workbench. Once the package is installed, you can, at the top of your Python script where you want to use this package, add an import statement: *import <packagename>* and then use the functions present in this package. Check the documentation and source code to know which functions and classes it exposes.


Creating an external package
============================
If you have found a useful external package, for example something on Pypi, we would invite you to share this package with other researchers in the workbench. To do this, click *Create New Package* / *Create an External Package*. Add the required information, such as a description and the URL. If the package is on PyPi, the workbench will automatically update you of new versions.
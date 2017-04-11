# Welcome to your experiment
This experiment was automatically initialized by the MOOC workbench.
Please take a moment to read how to get started.

## Getting started
In order to start development, we recommend the following best practices:

### Checking out this repository
In order to check out this repository, open up a terminal and make sure you've installed git:
- `sudo apt install git` on Ubuntu
- for macOS and Windows we recommend the use of the GitHub desktop app at https://desktop.github.com/
Make sure to commit and push your code often and make sure your commits are small. It helps for other researchers in the future to find what you've done.

### Work in a virtual environment
If you are using Python for your experiment, ensure you are working in a virtual environment and are using Python 3.
You can set up a virtualenv on Linux, macOS or Ubuntu bash for Windows 10 like so:
- First, make sure you've got all the required dependencies: `sudo apt install python3-pip virtualenv` or on macOS use Homebrew to install Python3 and then run `pip3 install virtualenv`
- Create a new virtualenv in your cwd: `virtualenv -p python3 my_virtualenv`
- Activate the virtual environment with `source my_virtualenv/bin/activate`
After you are done working, you can deactivate the virtualenv using `deactivate`

### Defining requirements
Use the MOOC workbench to install packages into your experiment. Once you have added some, click the button to update the dependencies in your repository.
You can then install the dependencies using:
- `git pull`
- `pip3 install -r requirements.txt`
Use the MOOC Workbench Marketplace to find useful resources and packages for your experiment and share ideas and thoughts about your experiment.

### File structure
Based on the steps you've chosen during the creation process of your experiment, we've went ahead and set up your experiment for you. In this experiment, you find the following files:
- main.py: This is the starting point for each step for your experiment
- test.py: Ensure to often test your code. While not always possible, do try to think of edge cases of your code, especially for the gathering, filtering and cleaning steps of your experiment. We've went ahead and set up your first test.
- settings.py: Here some settings for your experiment are defined, such as the location of your data, this folder for easy access and your data schema. Feel free to add other settings if you need them.

### Documentation
Ensure to write documentation early and often. To help you with this, we've added a tool called sphinx. You can just write your docs in your code and we'll take care of the rest.

### Testing and CI
TBD

### How am I doing?
The MOOC Workbench will monitor your progress with regards to use of version control, writing documentation, writing tests and defining dependencies and tell you how you are doing and offer tips to improve.

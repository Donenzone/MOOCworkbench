"""
.. module:: {PROJECTNAME}.{STEPFOLDER}.main
   :synopsis: This module is used to gather data for the MOOC experiment

.. moduleauthor:: {AUTHOR}
"""
import sys
sys.path.append('../')
sys.path.append('../..')
from settings import DATA_FOLDER


def main(data_sets=[]):
    """The starting point of this module for your experiment. Perform here all the actions needed for this module.

    :param data_sets: A list of CSV files present in the data/ folder with which to run this module.

    Returns True if successfully completed
    """
    print('Hello, world')
    return True


if __name__ == '__main__':
    main()

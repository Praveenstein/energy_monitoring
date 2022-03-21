# -*- coding: utf-8 -*-
"""
Command Line Input Getter
============================
Main Module for getting the command line arguments
This script requires the following modules be installed in the python environment
    * argparse - to handle command line arguments
This script contains the following function
    * get_input_arguments - to get the command line arguments
"""
# Built-in imports
import argparse
import json

INPUT_PARAMETER_FILE = "configs/input_parameters.json"


def get_input_arguments():
    """
    Function to get the input arguments from command line
    :return: args - arguments from the command line
    :rtype: argparse.Namespace
    """

    my_parser = argparse.ArgumentParser(allow_abbrev=False)
    my_parser.add_argument('--logfile', action='store', type=str, required=False)
    my_parser.add_argument('--dialect', action='store', type=str, required=False)
    my_parser.add_argument('--driver', action='store', type=str, required=False)
    my_parser.add_argument('--user', action='store', type=str, required=False)
    my_parser.add_argument('--host', action='store', type=str, required=False)
    my_parser.add_argument('--password', action='store', type=str, required=False)
    my_parser.add_argument('--database', action='store', type=str, required=False)
    my_parser.add_argument('--number', action='store', type=int, required=False)

    args = my_parser.parse_args()
    return args


def get_arguments_from_file():
    """
    INPUT ARGUMENTS FROM FILE
    =============================

    This function is used to read a json file containing some input arguments required to run
    this application.

    :return: The arguments required for running the application
    :rtype: dict
    """
    with open(INPUT_PARAMETER_FILE, 'r') as file:
        parameters = json.load(file)

    return parameters

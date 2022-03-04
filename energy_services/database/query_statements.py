# -*- coding: utf-8 -*-
"""
QUERY STATEMENTS
======================

Module for that contains common queries used in this project

This script requires that the following packages be installed within the Python
environment you are running this script in.

    * logging - to perform logging operations
"""

# Standard Imports
import logging

LOGGER = logging.getLogger(__name__)

# Some Global variables that we'll be using for storing the sql statements
LATEST_ENERGY_QUERY = "SELECT * FROM u759114105_energy_meter.energy_lmeasure ORDER BY id DESC LIMIT 1"

TOTAL_ENERGY_CONSUMED_TODAY_QUERY = "SELECT	" \
                              "(SELECT energy FROM u759114105_energy_meter.energy_lmeasure ORDER BY id DESC LIMIT 1)-" \
                              "(SELECT energy FROM u759114105_energy_meter.energy_lmeasure WHERE date = curdate()" \
                              "ORDER BY id LIMIT 1)"


def data_for_date_query(parameter, date):
    """
    Function that returns a sql query statement to return values for given parameter and date

    :param parameter: The parameter that needs to be queried such as energy, power
    :type parameter: str
    :param date: The date for which we need the values
    :type date: str
    :return: The sql query to get the values
    :rtype: str
    """
    statement = f"SELECT {parameter} FROM u759114105_energy_meter.energy_lmeasure WHERE date = '{date}' LIMIT 10"
    LOGGER.info(statement)
    return statement

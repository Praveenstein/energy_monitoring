# -*- coding: utf-8 -*-
"""
Module to perform Read operation
========================================

Module for reading records from the database

This script requires the following modules be installed in the python environment
    * logging - to perform logging operations

This script contains the following function
    *
"""

# Standard Imports
import logging
import time

# External Imports
from sqlalchemy import text
from sqlalchemy.engine.base import Engine

LOGGER = logging.getLogger(__name__)

# The below parameters represent a sample output of the json required for energy request api
ENERGY_PARAMETERS = {
    "id": "11438598",
    "date": "2022-03-03",
    "timestamp": "2022-03-03 16:35:24",
    "energy": "2100940",
    "power": "181.286",
    "avg_power_factor": "-0.1505",
    "avg_current": "1.6544",
    "avg_voltage": "242.575",
    "power_factor_1": "0.3025",
    "power_factor_2": "-0.0705",
    "power_factor_3": "0.0624",
    "phase_current_Ir": "1.7791",
    "phase_current_Iy": "1.462",
    "phase_current_Iz": "1.7223",
    "phase_voltage_Ir": "241.739",
    "phase_voltage_Iy": "241",
    "phase_voltage_Iz": "244.986",
    "frequency": "50.2218",
    "Energy_real": "0.100715"
}


def current_parameters_to_dictionary(records: list):
    """

    CONVERT DATABASE RECORDS TO DICTIONARY - ALL PARAMETERS
    ==========================================================

    This function is used to convert the raw database records resulted from the query to a standard dictionary (json)
    format to be sent to the client. This is specifically used for conversion required by
    "/energy_meter/current_update" api route.

    :param records: The results from SqlAlchemy query.

    :return: The dictionary of parameters with key and values matching from the latest database read
    :rtype: dict

    """

    parameters = ENERGY_PARAMETERS
    for result in records:

        # This for loop will result in modifying the parameters dictionary such that all the
        # Key values are updated with the recent one from the database
        for parameter, value in zip(parameters.keys(), result):
            parameters[parameter] = str(value)

    return parameters


def total_energy_to_dictionary(records: list):
    """

    CONVERT DATABASE RECORDS TO DICTIONARY - TOTAL ENERGY
    ==========================================================

    This function is used to convert the raw database records resulted from the query to a standard dictionary (json)
    format to be sent to the client. This is specifically used for conversion required by
    "/energy_meter/total_energy_today" api route.

    :param records: The results from SqlAlchemy query.

    :return: The dictionary consisting of total energy consumed today.
    :rtype: dict

    """

    parameters = {"total_energy": 0}
    for record in records:
        parameters["total_energy"] = record[0]

    return parameters


def date_wise_parameters_to_dictionary(dates: list[str], records: list):
    """

    CONVERT DATABASE RECORDS TO DICTIONARY - DATE WISE PARAMETERS
    =================================================================

    This function is used to convert the raw database records resulted from the query to a standard dictionary (json)
    format to be sent to the client. This is specifically used for conversion required by
    "/energy_meter/read_parameter_multiple" api route.

    :param dates: The list of dates for which the parameters are required to be read.
    :param records: The results from SqlAlchemy query.

    :return: The dictionary consisting of total energy consumed today.
    :rtype: dict

    """

    parameters_list = []
    for result in records:
        individual_data = []
        for row in result:
            individual_data.append(row[0])
        parameters_list.append(individual_data)

    parameters = {date: values for date, values in zip(dates, parameters_list)}
    return parameters


def read_rows(engine: Engine, statement: str):
    """

    Read Rows From Database
    ==============================

    Function used to Read records from the database based on the query statement passed as argument

    :param engine: The Sqlalchemy engine used to connect to the database
    :param statement: The query statement that is required to be executed

    :return: Returns the query result
    :rtype: list

    """

    # Opening a connection to the database
    with engine.connect() as conn:

        start_time = time.time()
        query_result = conn.execute(text(statement)).all()
        end_time = time.time()
        LOGGER.info("Total Time for Reading Data: {time} seconds".format(time=round((end_time - start_time), 4)))

    return query_result


def read_rows_multiple(engine: Engine, statements: list[str]):
    """

    Read Records Multiple Times
    ==============================

    :param engine: The Sqlalchemy engine used to connect to the database
    :param statements: An array containing the query statements that are required to be executed

    :return: Returns the query result
    :rtype: list

    """

    with engine.connect() as conn:

        start_time = time.time()
        query_results = [conn.execute(text(statement)).all() for statement in statements]
        end_time = time.time()
        LOGGER.info("Total Time for Reading Data: {time} Milliseconds".format(time=round((end_time - start_time), 4)))

    return query_results

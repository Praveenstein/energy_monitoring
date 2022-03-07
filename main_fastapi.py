# -*- coding: utf-8 -*-
"""

Main Module
========================

Main Module for doing basic operation with database

This script requires the following modules be installed in the python environment

    * logging - to perform logging operations

This script contains the following function

    * main - main function to call appropriate functions to perform the read operation to get the top customers

"""

# Standard imports
import logging

# External Imports
import uvicorn
from typing import Optional
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.engine.base import Engine

# User Imports
import energy_services.utils as helper
import energy_services.database as db

LOGGER = logging.getLogger(__name__)

APP = FastAPI()
DATABASE_ENGINE = None


def get_engine():
    """

    GET ENGINE
    ============

    This function is used as the generator function that is required (to send the engine) for a parameter(engine)
    inside the read_root api.

    :return: SqlAlchemy Engine
    :rtype: Engine

    """
    try:
        yield DATABASE_ENGINE
    except Exception as error:
        LOGGER.error(error)


class Item(BaseModel):
    name: str
    price: float
    test_int: int
    is_offer: Optional[bool] = None


@APP.get("/energy_meter/current_update")
def read_root(engine: Engine = Depends(get_engine)):
    """

    GET CURRENT PARAMETERS DATA
    ===============================

    This api is used to query the latest data from the database

    :param engine: The SqlAlchemy engine used to connect to the database
    :return: Return the current parameters in json/dictionary format
    :rtype: dict

    """
    statement = db.LATEST_ENERGY_QUERY
    database_records = db.read_rows(engine, statement)
    data = db.current_energy_to_dictionary(database_records)
    return data


@APP.get("/energy_meter/total_energy_today")
def read_total_energy(engine: Engine = Depends(get_engine)):
    """

    GET TOTAL ENERGY FOR TODAY
    ===============================

    This api is used to query the total energy consumed today (from today morning until now)

    :param engine: The SqlAlchemy engine used to connect to the database
    :return: Return the current parameters in json/dictionary format
    :rtype: dict

    """
    statement = db.TOTAL_ENERGY_CONSUMED_TODAY_QUERY
    database_records = db.read_rows(engine, statement)
    data = db.total_energy_to_dictionary(database_records)
    return data


@APP.get("/energy_meter/read_parameter_multiple")
def read_parameter_multiple(parameter: str, date_1: str, date_2: str, engine: Engine = Depends(get_engine)):
    """

    GET PARAMETER VALUES FOR GIVEN DATE
    =======================================

    This api is used to query the all the values of a given parameter for a given date(s). Which will be used
    for displaying a graph to compare the trend for the given 5 days.

    :param parameter: The parameter that needs to be read from the database ( such as power, energy etc)
    :param dates: The array of date (max 5) for which the given parameter values need to be returned
    :param engine: The SqlAlchemy engine used to connect to the database

    :return: Return the current parameters in json/dictionary format
    :rtype: dict

    """

    dates = [date_1, date_2]
    statements = [db.statement_for_date_query(parameter, date) for date in dates]
    records = db.read_rows_multiple(engine, statements)

    data = db.date_wise_parameters_to_dictionary(dates, records)
    return data


if __name__ == "__main__":

    # Getting the path for logging config using arparse
    log_config_file = helper.ARGUMENTS.logfile

    # Configuring logging
    helper.configure_logging(log_config_file)

    LOGGER.info("Creating Engine")

    # Getting a new engine
    DATABASE_ENGINE = db.create_new_engine(helper.ARGUMENTS.dialect, helper.ARGUMENTS.driver,
                                           helper.ARGUMENTS.user, helper.ARGUMENTS.password,
                                           helper.ARGUMENTS.host, helper.ARGUMENTS.database)

    uvicorn.run(APP, host="127.0.0.1", port=8000)

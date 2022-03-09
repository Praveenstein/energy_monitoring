# -*- coding: utf-8 -*-
"""
CORE ENERGY ROUTES MODULE
=====================================

This Module consists of api routes for get access to core energy meter routes such as total energy consumed today, etc

This script requires that the following packages be installed within the Python
environment you are running this script in.

    * logging - to perform logging operations

    *
"""

# Standard Imports
import logging

# External Imports
from fastapi import APIRouter, Depends
from sqlalchemy.engine.base import Engine

# User Imports
from .router_dependencies import get_current_active_user
import energy_services.database as db

LOGGER = logging.getLogger(__name__)

ROUTER = APIRouter(
    prefix="/energy_meter/energy_core",
    tags=["Core Energy Routes"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},)


@ROUTER.get("/current_update")
async def read_all_current_values(engine: Engine = Depends(db.get_engine)):
    """

    GET CURRENT PARAMETERS DATA
    ===============================

    This api is used to query the latest data from the database

    :param engine: The SqlAlchemy engine used to connect to the database.

    :return: Return the current parameters in json/dictionary format
    :rtype: dict

    """
    statement = db.LATEST_ALL_PARAMETER_QUERY
    database_records = db.read_rows(engine, statement)
    data = db.current_parameters_to_dictionary(database_records)
    return data


@ROUTER.get("/total_energy_today")
async def read_total_energy(engine: Engine = Depends(db.get_engine)):
    """

    GET TOTAL ENERGY FOR TODAY
    ===============================

    This api is used to query the total energy consumed today (from today morning until now)

    :param engine: The SqlAlchemy engine used to connect to the database.

    :return: Return the current parameters in json/dictionary format
    :rtype: dict

    """
    statement = db.TOTAL_ENERGY_CONSUMED_TODAY_QUERY
    database_records = db.read_rows(engine, statement)
    data = db.total_energy_to_dictionary(database_records)
    return data


@ROUTER.get("/read_parameter_multiple")
async def read_parameter_multiple(parameter: str, date_1: str, date_2: str, engine: Engine = Depends(db.get_engine)):
    """

    GET PARAMETER VALUES FOR GIVEN DATE
    =======================================

    This api is used to query the all the values of a given parameter for a given date(s). Which will be used
    for displaying a graph to compare the trend for the given 5 days.

    :param date_1: Date 1 for which all parameter values need to be sent
    :param date_2: Date 2 for which all parameter values need to be sent
    :param parameter: The parameter that needs to be read from the database ( such as power, energy etc)
    :param engine: The SqlAlchemy engine used to connect to the database

    :return: Return the current parameters in json/dictionary format
    :rtype: dict

    """

    # TODO: Change the parameter date_1, date_2 to something of array type

    dates = [date_1, date_2]
    statements = [db.statement_for_date_query(parameter, date) for date in dates]
    records = db.read_rows_multiple(engine, statements)

    data = db.date_wise_parameters_to_dictionary(dates, records)
    return data

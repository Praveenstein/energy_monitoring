# -*- coding: UTF-8 -*-
"""
INITIALIZATION MODULE FOR DATABASE OPERATIONS
=================================================

This is an initialization script for services available in this package
"""

# Importing necessary modules and functions to be used by modules using this package
from .engine import create_new_engine, get_engine, initialize_global_engine
from .read_operations import read_rows, read_rows_multiple, current_parameters_to_dictionary, \
    total_energy_to_dictionary, date_wise_parameters_to_dictionary
from .query_statements import LATEST_ALL_PARAMETER_QUERY, TOTAL_ENERGY_CONSUMED_TODAY_QUERY, \
    statement_for_date_query


USER_DB = {
    "cmti": {
        "username": "cmti",
        "full_name": "CMTI SMDDC",
        "email": "cmti@cmti.res.in",
        "hashed_password": "$2b$12$RCuPSrRoK15qgq14ShruqeRg0i2s4zuw2UHX80DBqewdqICHtdw2u",
        "disabled": False,
    }
}

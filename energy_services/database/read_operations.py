# -*- coding: utf-8 -*-
"""
Module to perform Read operation
========================================

Module for reading records from the database

This script requires the following modules be installed in the python environment
    * logging - to perform logging operations

This script contains the following function
    * perform_read_join - Function to perform read operation with the database using inner joins
"""
# Standard Imports
import logging

# External Imports
from sqlalchemy import text

LOGGER = logging.getLogger(__name__)


def read_rows(engine):
    with engine.connect() as conn:
        statement = "SELECT * FROM u759114105_energy_meter.energy_lmeasure LIMIT 3;"
        result = conn.execute(text(statement))
        for row in result:
            LOGGER.info(row)

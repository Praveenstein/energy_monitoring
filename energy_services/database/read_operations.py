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
import time

# External Imports
from sqlalchemy import text

LOGGER = logging.getLogger(__name__)


def read_rows(engine, statement):
    with engine.connect() as conn:

        start_time = time.time()
        result = conn.execute(text(statement))
        end_time = time.time()
        LOGGER.info("Total Time for Reading Data: {time} ms".format(time=(end_time - start_time)*1000))
        for row in result:
            LOGGER.info(row)


def read_rows_multiple(engine, statements):
    with engine.connect() as conn:

        start_time = time.time()
        results = [conn.execute(text(statement)) for statement in statements]
        end_time = time.time()
        LOGGER.info("Total Time for Reading Data: {time} Milliseconds".format(time=(end_time - start_time)*1000))
        for result in results:
            LOGGER.info("\n Printing Result \n ============================================== \n")
            for row in result:
                LOGGER.info(row)
            LOGGER.info("\n")

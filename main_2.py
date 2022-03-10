# -*- coding: utf-8 -*-
"""
Main Module
=============================================================
Main Module for doing basic operation with database

This script requires the following modules be installed in the python environment

    * logging - to perform logging operations

This script contains the following function

    * main - main function to call appropriate functions to perform the read operation.
"""

# Standard imports
import logging

# User Imports
import energy_services.utils as helper
import energy_services.database as db

LOGGER = logging.getLogger(__name__)


def main():
    """
    Main function to read records from the database

    :return: Nothing
    :rtype: None
    """

    # Getting the path for logging config using arparse
    log_config_file = helper.ARGUMENTS.logfile

    # Configuring logging
    helper.configure_logging(log_config_file)

    LOGGER.info("Creating Engine")
    # Getting a new engine
    engine = db.create_new_engine(helper.ARGUMENTS.dialect, helper.ARGUMENTS.driver,
                                  helper.ARGUMENTS.user, helper.ARGUMENTS.password,
                                  helper.ARGUMENTS.host, helper.ARGUMENTS.database)

    statement = db.LATEST_ALL_PARAMETER_QUERY
    #statement = "SELECT 2"
    database_records = db.read_rows(engine, statement)
    data = db.current_parameters_to_dictionary(database_records)

    LOGGER.info(data)

    engine.dispose()
    LOGGER.info("Engine disposed")


if __name__ == '__main__':
    main()

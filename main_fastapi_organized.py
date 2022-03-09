# -*- coding: utf-8 -*-
"""

Main Module
===============

Main Module for doing basic operation with database

This script requires the following modules be installed in the python environment

    * logging - to perform logging operations

This script contains the following function

    * main - main function to call appropriate functions

"""

# Standard imports
import logging

# External Imports
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# User Imports
import energy_services.utils as helper
import energy_services.database as db
from energy_services.routers import core_energy_routes, security_routes, user_routes

LOGGER = logging.getLogger(__name__)


def main():
    """
    MAIN FUNCTION
    ===================

    This is the main function that get the arguments from the cli, creates a database engine,
    and creates a fastapi app and runs the uvicorn server

    :return: Nothing
    :rtype: None
    """

    # Getting the path for logging config using arparse
    log_config_file = helper.ARGUMENTS.logfile

    # Configuring logging
    helper.configure_logging(log_config_file)

    LOGGER.info("Creating Engine")

    # Getting a new engine
    db_engine = db.create_new_engine(helper.ARGUMENTS.dialect, helper.ARGUMENTS.driver,
                                     helper.ARGUMENTS.user, helper.ARGUMENTS.password,
                                     helper.ARGUMENTS.host, helper.ARGUMENTS.database)

    # Initializing the global engine variable to the newly created sqlalchemy engine created above
    db.initialize_global_engine(db_engine)

    LOGGER.info("Engine Creation Over")

    LOGGER.info("Creating the FastApi application")

    app = FastAPI()

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(core_energy_routes.ROUTER)
    app.include_router(security_routes.ROUTER)
    app.include_router(user_routes.ROUTER)

    uvicorn.run(app, host="172.18.7.27", port=8000)


if __name__ == "__main__":
    main()

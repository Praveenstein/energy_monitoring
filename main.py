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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# User Imports
import energy_services.utils as helper
import energy_services.database as db
from energy_services.routers import core_energy_routes, security_routes, user_routes

LOGGER = logging.getLogger(__name__)


ARGUMENTS = helper.get_arguments_from_file()
# Getting the path for logging config using arparse
LOG_CONFIG_FILE = ARGUMENTS["logfile"]
# Configuring logging
helper.configure_logging(LOG_CONFIG_FILE)

LOGGER.info("Creating Engine")

# Getting a new engine
DB_ENGINE = db.create_new_engine(ARGUMENTS["dialect"], ARGUMENTS["driver"],
                                 ARGUMENTS["user"], ARGUMENTS["password"],
                                 ARGUMENTS["host"], ARGUMENTS["database"])

# Initializing the global engine variable to the newly created sqlalchemy engine created above
db.initialize_global_engine(DB_ENGINE)

LOGGER.info("Engine Creation Over")

LOGGER.info("Creating the FastApi application")

APP = FastAPI()

ORGINS = ["*"]

APP.add_middleware(
    CORSMiddleware,
    allow_origins=ORGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APP.include_router(core_energy_routes.ROUTER)
APP.include_router(security_routes.ROUTER)
APP.include_router(user_routes.ROUTER)

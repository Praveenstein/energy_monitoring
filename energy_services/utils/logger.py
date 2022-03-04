# -*- coding: utf-8 -*-
"""
Logging Configuration
==========================
Main Module for configuring logger

This script requires the following modules be installed in the python environment
    * logging - to perform logging operations
    * json - to load json files

This script contains the following function
    * configure_logging - to configure logging
"""
import logging.config
import json


LOGGER = logging.getLogger(__name__)


def configure_logging(filepath):
    """
    Function to configure logging
    :return: None
    """
    try:
        with open(filepath, 'r') as file_object:
            config_data = json.load(file_object)
    except FileNotFoundError as err:
        LOGGER.error(err)
        raise

    logging.config.dictConfig(config_data)

    LOGGER.info("Configured Logging")

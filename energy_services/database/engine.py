# -*- coding: utf-8 -*-
""" Module for creating Engine and session maker factory
This script requires that the following packages be installed within the Python
environment you are running this script in.

    * logging - to perform logging operations

    * sqlalchemy - Package used to connect to a database and do SQL operations using orm_queries
"""
# Standard Imports
import logging

# External Imports
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine

LOGGER = logging.getLogger(__name__)

GLOBAL_DATABASE_ENGINE = None


def create_new_engine(dialect, driver, user, password, host, database):
    """
    Function to Create new engine from given input arguments
    ===================================================================

    :param dialect: The database dialect being used
    :type dialect: str
    :param driver: The driver used to connect to the give database dialect
    :type driver: str
    :param user: The user to login into the database
    :type user: str
    :param password: The password of the user to login into the database
    :type password: str
    :param host: The host ID
    :type host: str
    :param database: The database name to connect to
    :type database: str
    :return: New engine configured with given parameters
    :rtype: :class:`sqlalchemy.engine.create_engine`
    """
    try:

        if not all(map(lambda arg: True if issubclass(type(arg), str) else False, [dialect, driver, user, password,
                                                                                   host, database])):
            raise AttributeError("Invalid attribute type, should be string")

        connection_string = dialect + "+" + driver + "://" + user + ":" + password + "@" + host + "/" + \
                            database + "?charset=utf8mb4"

        engine = create_engine(connection_string, echo=False)
        LOGGER.info("Created Engine for {dialect} Connection at : {ip} using "
                    "{driver} to the {database} Database".format(dialect=dialect, ip=host, driver=driver,
                                                                 database=database))
        return engine
    except AttributeError as err:
        LOGGER.error(err)
        raise


def initialize_global_engine(engine: Engine):
    """
    Function used to initialize the global engine variable ( from the main script)

    :param engine: The sqlalchemy engine used to connect to the database

    :return: Nothing
    :rtype: None
    """

    global GLOBAL_DATABASE_ENGINE
    GLOBAL_DATABASE_ENGINE = engine


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
        yield GLOBAL_DATABASE_ENGINE
    except Exception as error:
        LOGGER.error(error)

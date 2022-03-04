# -*- coding: utf-8 -*-
"""
Table Models
===================

Module that contains python class for sql table mappings

This script requires that the following packages be installed within the Python
environment you are running this script in.
    * sqlalchemy - Package used to connect to a database and do SQL operations using orm_queries
"""
# Standard Imports
import logging

# External Imports
from sqlalchemy import MetaData, Table, Column, Integer, String


LOGGER = logging.getLogger(__name__)

metadata_obj = MetaData()


def reflect_tables(engine):
    some_table = Table("some_table", metadata_obj, autoload_with=engine)

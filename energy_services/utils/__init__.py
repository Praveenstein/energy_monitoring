# -*- coding: UTF-8 -*-
"""
Helper
=============
This is an initialization module for helper utilities
"""

# Importing necessary modules and functions to be used by modules using this package
from energy_services.utils.input_getter import get_input_arguments
from energy_services.utils.logger import configure_logging


ARGUMENTS = get_input_arguments()

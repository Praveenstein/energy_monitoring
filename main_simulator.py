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
import socket
import time

# External Imports
import pytz


# User Imports
import energy_services.utils as helper
import energy_services.devices as devices


LOGGER = logging.getLogger(__name__)

ARGUMENTS = helper.get_arguments_from_file()
# Getting the path for logging config using arparse
LOG_CONFIG_FILE = ARGUMENTS["logfile"]
# Configuring logging
helper.configure_logging(LOG_CONFIG_FILE)


def main():

    ist = pytz.timezone('Asia/Kolkata')
    tcp_server = "127.0.0.1"  # The server's hostname or IP address
    tcp_server_port = 8094  # The port used by the server
    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_object:
            LOGGER.info("Socket Created")
            socket_object.connect((tcp_server, tcp_server_port))
            LOGGER.info("Connection Created")

            while True:
                choice_of_states = devices.machine_states()
                raw_data = devices.generate_current_data(choice_of_states)

                for index, data in enumerate(raw_data):
                    local_time = time.time_ns()
                    message = f"energy,device=htm_stallion_200 current={round(data, 4)},number={index}" \
                              f" {local_time}\n"
                    socket_object.sendall(message.encode("utf8"))
                    LOGGER.info(message)
                    time.sleep(2)
    except Exception as error:
        LOGGER.exception(error)


if __name__ == "__main__":
    main()


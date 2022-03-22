# -*- coding: utf-8 -*-
"""
DEVICE SIMULATOR
======================

Module for that contains functions to simulate a cnc machine

This script requires that the following packages be installed within the Python
environment you are running this script in.

    * logging - to perform logging operations
"""

# Standard Imports
import logging
import random
import socket
import time
import json

# External Imports
import plotly.graph_objects as go

LOGGER = logging.getLogger(__name__)


def machine_states():

    choice_of_states = dict()

    # ((lower limit, upper limit of current value), (lower time, upper time),
    # (lower_average_current, upper_average_current),
    # (lower_peak_current, upper_peak_current), (key value mapping for machine status to code))
    # (0, 1, 2) ----> (machine off, machine on, machine production)
    choice_of_states["MACHINE_OFF"] = ((0, 0.8), (180, 600), (0.25, 0.50), (0.65, 0.78), 0)
    choice_of_states["MACHINE_ON"] = ((0.81, 3.5), (300, 900), (3.2, 3.5), (5.5, 7.5), 1)
    choice_of_states["MACHINE_PRODUCTION"] = ((3.51, 10), (480, 1200), (3.51, 4.5), (10, 17), 2)

    return choice_of_states


def generate_points(time_duration, status):

    random_current_data = [random.uniform(status[2][0], status[2][1]) for _ in range(time_duration)]
    noise_integers = [random.randint(0, time_duration - 1) for _ in range(10)]
    for noise in noise_integers:
        random_current_data[noise] = random.uniform(status[3][0], status[3][1])
    return random_current_data


def generate_current_data(choice_of_states):

    # (time of change of machine status, state)
    overall_machine_status = [(0, 0), (181, 1)]
    raw_data = []

    initial_off_points = generate_points(180, choice_of_states["MACHINE_OFF"])
    initial_on_points = generate_points(300, choice_of_states["MACHINE_ON"])
    closing_off_points = generate_points(180, choice_of_states["MACHINE_OFF"])

    raw_data.extend(initial_off_points)
    raw_data.extend(initial_on_points)

    remaining_time = 28800
    previous_state = "MACHINE_ON"
    previous_time_for_state_change = 481

    while True:
        status_key = random.choice(list(choice_of_states.keys()))
        if (previous_state == "MACHINE_OFF") and (status_key == "MACHINE_PRODUCTION"):
            continue
        if (previous_state == "MACHINE_PRODUCTION") and (status_key == "MACHINE_OFF"):
            continue

        current_machine_status = choice_of_states[status_key]
        machining_time = random.randint(current_machine_status[1][0], current_machine_status[1][1])

        LOGGER.info("============================")
        LOGGER.info(f"Current Status: {status_key}")
        LOGGER.info(f"Previous Status: {previous_state}")
        LOGGER.info(f"Time: {machining_time}")
        remaining_time -= machining_time

        LOGGER.info(f"Remaining Time: {remaining_time}")

        LOGGER.info("==============================")

        if remaining_time - 180 < 0:
            remaining_time += machining_time
            break

        if previous_state == status_key:
            previous_time_for_state_change += machining_time
        else:
            overall_machine_status.append((previous_time_for_state_change, current_machine_status[-1]))
            previous_time_for_state_change += machining_time

        points = generate_points(machining_time, current_machine_status)
        raw_data.extend(points)
        previous_state = status_key

    closing_on_points = generate_points(remaining_time - 180, choice_of_states["MACHINE_ON"])
    raw_data.extend(closing_on_points)
    raw_data.extend(closing_off_points)

    overall_machine_status.append((overall_machine_status[-1][0] + remaining_time, 1))
    overall_machine_status.append((overall_machine_status[-1][0] + 180, 0))

    return raw_data


def main():

    tcp_server = "127.0.0.1"  # The server's hostname or IP address
    tcp_server_port = 65432  # The port used by the server
    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_object:
            socket_object.connect((tcp_server, tcp_server_port))

            for _ in range(10):
                choice_of_states = machine_states()
                raw_data = generate_current_data(choice_of_states)

                for data in raw_data:

                    message = {"device": "htm_stallion_200",
                               "current": data,
                               "time": time.time()}
                    message = json.dumps(message)
                    socket_object.sendall(message.encode())
                    #data = socket_object.recv(1024)
                    #print(f"Received {data.decode()}")
                    time.sleep(2)
    except Exception as error:
        LOGGER.exception(error)


if __name__ == "__main__":
    main()

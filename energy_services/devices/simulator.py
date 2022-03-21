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

CHOICE_OF_STATUS = dict()

# ((lower limit, upper limit of current value), (lower time, upper time),
# (lower_average_current, upper_average_current),
# (lower_peak_current, upper_peak_current), (key value mapping for machine status to code))
# (0, 1, 2) ----> (machine off, machine on, machine production)
CHOICE_OF_STATUS["MACHINE_OFF"] = ((0, 0.8), (180, 600), (0.25, 0.50), (0.65, 0.78), 0)
CHOICE_OF_STATUS["MACHINE_ON"] = ((0.81, 3.5), (300, 900), (3.2, 3.5), (5.5, 7.5), 1)
CHOICE_OF_STATUS["MACHINE_PRODUCTION"] = ((3.51, 10), (480, 1200), (3.51, 4.5), (10, 17), 2)


def generate_points(time_duration, status):

    random_current_data = [random.uniform(status[2][0], status[2][1]) for _ in range(time_duration)]
    noise_integers = [random.randint(0, time_duration - 1) for _ in range(10)]
    for noise in noise_integers:
        random_current_data[noise] = random.uniform(status[3][0], status[3][1])
    return random_current_data


def generate_current_data():

    # (machine status time change, state)
    MACHINE_STATUS = [(0, 0), (181, 1)]
    RAW_DATA = []

    initial_off_points = generate_points(180, CHOICE_OF_STATUS["MACHINE_OFF"])
    initial_on_points = generate_points(300, CHOICE_OF_STATUS["MACHINE_ON"])
    closing_off_points = generate_points(180, CHOICE_OF_STATUS["MACHINE_OFF"])

    RAW_DATA.extend(initial_off_points)
    RAW_DATA.extend(initial_on_points)

    REMAINING_TIME = 28800
    PREVIOUS_STATE = "MACHINE_ON"
    PREVIOUS_TIME_FOR_STATE_CHANGE = 481

    while True:
        status_key = random.choice(list(CHOICE_OF_STATUS.keys()))
        if (PREVIOUS_STATE == "MACHINE_OFF") and (status_key == "MACHINE_PRODUCTION"):
            continue
        if (PREVIOUS_STATE == "MACHINE_PRODUCTION") and (status_key == "MACHINE_OFF"):
            continue

        machine_status = CHOICE_OF_STATUS[status_key]
        machining_time = random.randint(machine_status[1][0], machine_status[1][1])

        print("============================")
        print("Current Status: ", status_key)
        print("Previous Status: ", PREVIOUS_STATE)
        print("Time: ", machining_time)
        REMAINING_TIME -= machining_time

        print("Remaining Time: ", REMAINING_TIME)

        print("==============================")

        if REMAINING_TIME - 180 < 0:
            REMAINING_TIME += machining_time
            break

        if PREVIOUS_STATE == status_key:
            PREVIOUS_TIME_FOR_STATE_CHANGE += machining_time
        else:
            MACHINE_STATUS.append((PREVIOUS_TIME_FOR_STATE_CHANGE, machine_status[-1]))
            PREVIOUS_TIME_FOR_STATE_CHANGE += machining_time

        points = generate_points(machining_time, machine_status)
        print("points: ", len(points))
        RAW_DATA.extend(points)
        PREVIOUS_STATE = status_key

    closing_on_points = generate_points(REMAINING_TIME - 180, CHOICE_OF_STATUS["MACHINE_ON"])
    RAW_DATA.extend(closing_on_points)
    RAW_DATA.extend(closing_off_points)

    MACHINE_STATUS.append((MACHINE_STATUS[-1][0] + REMAINING_TIME, 1))
    MACHINE_STATUS.append((MACHINE_STATUS[-1][0] + 180, 0))

    return RAW_DATA


def main():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as device_Socket:

        host = "localhost"
        port = 1234
        device_Socket.connect((host, port))

        while True:

            raw_data = generate_current_data()

            for data in raw_data:
                message = {"device": "htm_stallion_200",
                           "current": data,
                           "time": time.time()}
                message = json.dumps(message)
                device_Socket.sendall(message.encode())
                print("Sent")
                time.sleep(1)


if __name__ == "__main__":
    main()

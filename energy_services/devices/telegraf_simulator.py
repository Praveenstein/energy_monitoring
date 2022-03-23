# -*- coding: utf-8 -*-
"""
DEVICE SIMULATOR
======================

Module for that contains functions to simulate a cnc machine

This script requires that the following packages be installed within the Python
environment you are running this script in.

    * logging - to perform logging operations
"""

import logging
import socket

LOGGER = logging.getLogger(__name__)

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            print(f"Received {data.decode()}")
            if not data:
                break
            #conn.sendall(data)

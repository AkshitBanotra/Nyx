#!/usr/bin/env python3

import socket
import os
import subprocess
from shared import llm_listen

socket_path = "/tmp/my_socket"

# Remove old socket file if it exists
try:
    os.unlink(socket_path)
except FileNotFoundError:
    pass

# Create Unix domain socket
server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind socket to filesystem path
server.bind(socket_path)

# Listen for connections
server.listen(1)

print("Server is listening for incoming connections.")

# Accept a client
connection, _ = server.accept()
#print(connection)

try:
    #print("Client connected.")

    while True:
        # Receive data
        data = connection.recv(1024)

        # Client closed the connection
        if not data:
            break

        if data == b'LLM_TOGGLE':
            print("Data recieved: ", data)
            subprocess.run(["notify-send", "[NYX]", "Listening..."])
            llm_listen = True

        #print("Received data:", data.decode())

        # Send response
        #response = f"Yo! I recieved that message: {data.decode()}"
        #connection.sendall(response.encode())

finally:
    connection.close()
    server.close()

    # Remove socket file
    try:
        os.unlink(socket_path)
    except FileNotFoundError:
        pass

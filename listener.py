import os
import socket
import subprocess

from dotenv import load_dotenv

load_dotenv()

# Define host and port to listen on
HOST = "127.0.0.1"
PORT = int(os.getenv("SERVER_CONTAINER_LISTENER_PORT"))


def shell_command(cmd):
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, encoding="utf-8"
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None


def get_server_status():
    code = shell_command("pidof java")
    return "RUNNING" if code else "TERMINATED"


def process_request(cmd):
    # Process the received string and generate a response
    cmd = cmd.strip()
    match cmd:
        case "start":
            return "Server started"

        case "stop":
            return "Server stopped"
        case "info":
            return '{"status": "' + get_server_status() + '"}'
        case _:
            return f"Not found {cmd} command in server listener"


# Create a TCP/IP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Bind the socket to the address and port
    server_socket.bind((HOST, PORT))

    # Listen for incoming connections
    server_socket.listen()
    print("Server is listening...")

    while True:
        # Accept incoming connection
        conn, addr = server_socket.accept()
        with conn:
            print("Connected by", addr)
            # Receive data from the client
            data = conn.recv(1024).decode()
            if not data:
                break
            print("Received:", data)

            # Process the request
            response = process_request(data)

            # Send response to the client
            conn.sendall(response.encode())
            print("Sent:", response)

            # Close the connection
            conn.close()

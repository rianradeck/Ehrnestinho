import json
import os
import socket

from dotenv import load_dotenv

import minecraft.cloud as cloud
import minecraft.rcon as rcon

load_dotenv()

MACHINE_MODE = os.getenv("MACHINE_MODE")


def send_tcp_command(ip, port, cmd):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:
        _socket.connect((ip, port))
        _socket.sendall(cmd.encode())
        response = _socket.recv(1024).decode()
        _socket.close()

        return response


class Server:
    def rcon(self, cmd):
        return rcon.command(cmd)


class GCServer(Server):
    def start(self):
        return cloud.start_vm()

    def stop(self):
        return cloud.stop_vm()

    def get_info(self):
        return cloud.get_info()


class LocalServer(Server):
    def __init__(self):
        self.ip = os.getenv("SERVER_CONTAINER_NAME")
        self.port = int(os.getenv("SERVER_CONTAINER_LISTENER_PORT"))
        rcon.change_server_ip(self.ip)

    def start(self):
        response = send_tcp_command(self.ip, self.port, "start")
        return response

    def stop(self):
        response = send_tcp_command(self.ip, self.port, "stop")
        return response

    def get_info(self):
        response = send_tcp_command(self.ip, self.port, "info")
        return json.loads(response)


def get_server():
    if MACHINE_MODE == "local":
        return LocalServer()
    if MACHINE_MODE == "virtual":
        return GCServer()
    return None


if __name__ == "__main__":
    server = LocalServer()
    response = server.get_info()
    print(response)

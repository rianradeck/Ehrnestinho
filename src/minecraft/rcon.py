import os

from dotenv import load_dotenv
from mcrcon import MCRcon

load_dotenv()
RCON_PASSWORD = os.getenv("RCON_PASSWORD")
SERVER_IP = os.getenv("SERVER_IP")


def change_server_ip(new_ip):
    global SERVER_IP
    SERVER_IP = new_ip
    return


def command(cmd):
    print("rcon", SERVER_IP)
    with MCRcon(SERVER_IP, RCON_PASSWORD) as mcr:
        resp = mcr.command(cmd)
        return resp


if __name__ == "__main__":
    print(command("list"))

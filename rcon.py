import os

from dotenv import load_dotenv
from mcrcon import MCRcon

load_dotenv()
RCON_PASSWORD = os.getenv("RCON_PASSWORD")
SERVER_IP = os.getenv("SERVER_IP")


def command(cmd):
    with MCRcon(SERVER_IP, RCON_PASSWORD) as mcr:
        resp = mcr.command(cmd)
        return resp

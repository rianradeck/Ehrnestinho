from pathlib import Path

from discord.ext import commands

import minecraft.rcon as rcon
from minecraft.server import get_server
from tasks import verify_server
from utils import call_admin

client: commands.Bot = None
server = get_server()
server_admins = []
root_path = Path(__file__).parent.parent.parent


def load_minecraft(_client: commands.Bot, _server_admins: list):
    global client
    global server_admins
    client = _client
    server_admins = _server_admins

    load_commands()


def load_commands():
    client.hybrid_command()(mine)


async def mine(ctx: commands.Context, arg):
    try:
        args = arg.split()
        match args[0]:
            case "start":
                code = (
                    server.start()
                )  # Only returns 0 or 200, else raises an exception

                if code == 0:
                    await ctx.send("Server is already started")
                if code == 200:
                    message = await ctx.send("Server is starting")
                    verify_server.start(message, "RUNNING")

            case "stop":
                code = (
                    server.stop()
                )  # Only returns 0 or 200, else raises an exception

                if code == 0:
                    await ctx.send("Server is already stopped")
                if code == 200:
                    message = await ctx.send("Server is stopping")
                    verify_server.start(message, "TERMINATED")

            case "help":
                with open(
                    root_path / "resources" / "help_message.txt"
                ) as file:
                    text_content = file.read()
                await ctx.send(text_content)

            case "status":
                info = server.get_info()
                await ctx.send(f"Server status is {info['status']}")

            case "rcon":
                if ctx.message.author not in server_admins:
                    await ctx.send(
                        f"{ctx.message.author.mention} "
                        "does not have rcon permission"
                    )
                    return

                if len(args) < 2:
                    await ctx.send("No command was given")
                    return

                response = rcon.command(" ".join(args[1:]))
                if response == "":
                    response = "OK"

                await ctx.send(f"Server response: {response}")

            case _:
                await ctx.send(f"Command {args[0]} not found")
    except Exception as e:
        await call_admin(ctx, e)

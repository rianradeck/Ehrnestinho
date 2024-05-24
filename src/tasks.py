import discord
from discord.ext import commands, tasks

import minecraft.rcon as rcon
from minecraft.server import get_server
from utils import call_admin

client: commands.Bot = None
server = get_server()
loading = ["|", "/", "-", "\\"]


def load_tasks(_client: commands.Bot):
    global client
    client = _client
    refresh_activity.start()


@tasks.loop(seconds=60, count=None)
async def refresh_activity():
    server_status = server.get_info()["status"]

    if server_status == "TERMINATED":
        await client.change_presence(
            activity=discord.Game(name="!mine help"),
            status=discord.Status.idle,
        )
    elif server_status == "RUNNING":
        online_players = f"{rcon.command('list')[10]} players online"
        await client.change_presence(
            activity=discord.Game(name=f"at Ehrnesto - {online_players}"),
            status=discord.Status.online,
        )


@tasks.loop(seconds=1.5, count=None)
async def verify_server(message, status_to_break):
    _status = "starting" if status_to_break == "RUNNING" else "stopping"
    _loading_char = loading[verify_server.current_loop % 4]
    await message.edit(content=f"Server is {_status} {_loading_char}")
    try:
        server_status = server.get_info()["status"]

        if server_status == status_to_break:
            await message.edit(content=f"Server {status_to_break}!")
            verify_server.cancel()

        if verify_server.current_loop == 40:
            await message.edit(content="Server timed out!")
            verify_server.cancel()
    except Exception as e:
        verify_server.cancel()
        await call_admin(message.channel, e)

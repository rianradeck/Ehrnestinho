import os

import discord
import discord.ext
import discord.ext.tasks
from discord.ext import commands, tasks
from dotenv import load_dotenv

import rcon
from server import get_server

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
ADMIN_ROLE = os.getenv("ADMIN_ROLE")
SERVER_ADMINS_LIST = os.getenv("SERVER_ADMINS_LIST")

client = commands.Bot(
    command_prefix="!",
    intents=discord.Intents.all(),
    activity=discord.Game(name="!mine help"),
    status=discord.Status.idle,
)
loading = ["|", "/", "-", "\\"]

server_admins_names = SERVER_ADMINS_LIST
server_admins = []

server = get_server()


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")

    guild = discord.utils.get(client.guilds, name=GUILD)

    for member in guild.members:
        if member.name in server_admins_names:
            server_admins.append(member)

    print("Ehrnesto admins:", server_admins)

    if guild.name == GUILD:
        print(
            f"{client.user} is connected to the following guild:\n"
            f"{guild.name}(id: {guild.id})"
        )

    synced = await client.tree.sync()
    print(f"Synced {[cmd for cmd in synced]}.")

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


@client.hybrid_command()
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
                    message = await ctx.send(
                        f"Server is starting {loading[0]}"
                    )
                    verify_server.start(message, "RUNNING")

            case "stop":
                code = (
                    server.stop()
                )  # Only returns 0 or 200, else raises an exception

                if code == 0:
                    await ctx.send("Server is already stopped")
                if code == 200:
                    message = await ctx.send(
                        f"Server is stopping {loading[0]}"
                    )
                    verify_server.start(message, "TERMINATED")

            case "help":
                with open("./help_message.txt") as file:
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


async def call_admin(ctx, e=None):
    guild = discord.utils.get(client.guilds, name=GUILD)
    admin_role = discord.utils.get(guild.roles, name=ADMIN_ROLE)
    await ctx.send(
        "Something went very wrong, "
        f"call an {admin_role.mention}\nException: {e}"
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


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)

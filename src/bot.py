import os

import discord
import discord.ext
import discord.ext.tasks
from discord.ext import commands
from dotenv import load_dotenv

import tasks
from minecraft import minecraft
from music import music

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_ADMINS_LIST = os.getenv("SERVER_ADMINS_LIST")
GUILD = os.getenv("DISCORD_GUILD")

server_admins_names = SERVER_ADMINS_LIST
server_admins = []

client = commands.Bot(
    command_prefix="!",
    intents=discord.Intents.all(),
    activity=discord.Game(name="!mine help"),
    status=discord.Status.idle,
)


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

    tasks.load_tasks(client)
    minecraft.load_minecraft(client, server_admins)
    music.load_music(client)

    print(client.all_commands.items())

    synced = await client.tree.sync()
    print(f"Synced {[cmd for cmd in synced]}.")


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)

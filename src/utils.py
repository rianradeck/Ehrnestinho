import os

import discord
from discord.ext import commands

GUILD = os.getenv("DISCORD_GUILD")
ADMIN_ROLE = os.getenv("ADMIN_ROLE")

client: commands.Bot = None


def load(_client: commands.Bot):
    global client
    client = _client


async def call_admin(ctx, e=None):
    guild = discord.utils.get(client.guilds, name=GUILD)
    admin_role = discord.utils.get(guild.roles, name=ADMIN_ROLE)
    await ctx.send(
        "Something went very wrong, "
        f"call an {admin_role.mention}\nException: {e}"
    )

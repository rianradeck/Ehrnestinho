import os

import discord
import discord.ext
import discord.ext.tasks
from discord.ext import commands, tasks
from dotenv import load_dotenv

import cloud

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")
ADMIN = os.getenv("ADMIN")

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())
loading = ["|", "/", "-", "\\"]


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")

    guild = discord.utils.get(client.guilds, name=GUILD)

    if guild.name == GUILD:
        print(
            f"{client.user} is connected to the following guild:\n"
            f"{guild.name}(id: {guild.id})"
        )

    synced = await client.tree.sync()
    print(f"Synced {[cmd for cmd in synced]}.")


@client.hybrid_command()
async def mine(ctx: commands.Context, arg):
    try:
        match arg:
            case "start":
                code = (
                    cloud.start_vm()
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
                    cloud.stop_vm()
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
                info = cloud.get_info()
                await ctx.send(f"Server status is {info['status']}")

            case "test":
                pass
    except Exception as e:
        await call_admin(ctx, e)


async def call_admin(ctx, e=None):
    guild = discord.utils.get(client.guilds, name=GUILD)
    admin_role = discord.utils.get(guild.roles, name=ADMIN)
    await ctx.send(
        f"Something went very wrong, call an {admin_role.mention}\nException: {e}"
    )


@tasks.loop(seconds=1.5, count=None)
async def verify_server(message, status_to_break):
    await message.edit(
        content=f"Server is {'starting' if status_to_break == 'RUNNING' else 'stopping'} {loading[verify_server.current_loop % 4]}"
    )
    try:
        server_status = cloud.get_info()["status"]

        if server_status == status_to_break:
            await message.edit(content=f"Server {status_to_break}!")
            verify_server.cancel()

        if verify_server.current_loop == 40:
            await message.edit(content="Server timed out!")
            verify_server.cancel()
    except Exception as e:
        verify_server.cancel()
        await call_admin(message.channel, e)


client.run(TOKEN)

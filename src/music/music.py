import asyncio
import copy
import os
from pathlib import Path
from threading import Thread

import discord
import pytubefix
from discord.ext import commands

from utils import call_admin

song_queue = []
client: commands.Bot = None
root_path = Path(__file__).parent.parent.parent


def load_music(_client: commands.Bot):
    global client
    client = _client

    load_commands()


def load_commands():
    client.command()(music)


QUEUE_TEXT = r"""
   _____
  / ____|
 | (___   ___  _ __   __ _    __ _ _   _  ___ _   _  ___
  \___ \ / _ \| '_ \ / _` |  / _` | | | |/ _ \ | | |/ _ \
  ____) | (_) | | | | (_| | | (_| | |_| |  __/ |_| |  __/
 |_____/ \___/|_| |_|\__, |  \__, |\__,_|\___|\__,_|\___|
                      __/ |     | |
                     |___/      |_|

"""


def download_song(song: pytubefix.YouTube, filename):
    audiostreams = song.streams.filter(only_audio=True, mime_type="audio/mp4")
    audiostreams[0].download(filename=filename)


def add_to_queue(song: pytubefix.YouTube):
    song_id = song.watch_url[song.watch_url.find("=") + 1 :]
    song_queue.append((song, song_id))
    refresh_downloads()


def refresh_downloads():
    for idx, (song, song_id) in enumerate(song_queue):
        if idx > 2:
            break
        song_path = (
            root_path / "resources" / "downloaded_songs" / f"{song_id}.mp4"
        )
        if not os.path.exists(song_path):
            print(f"Downloading {idx}, {song.title}, {song_id}")
            t = Thread(
                target=download_song,
                args=[copy.deepcopy(song), copy.deepcopy(song_path)],
                daemon=True,
            )
            t.run()


def delete_all_downloaded_songs():
    downloaded_songs_path = root_path / "resources" / "downloaded_songs"
    for song_id in os.listdir(downloaded_songs_path):
        cur_song_path = downloaded_songs_path / song_id
        print("deleting", cur_song_path)
        os.remove(cur_song_path)


async def music(ctx: commands.Context, *args):
    global song_queue

    if ctx.author.voice is None:
        await ctx.send("Please connect to a voice channel")
        return

    subcommand, *query = args
    query = (" " if len(query) > 1 else "").join(query)
    voice_channel = ctx.author.voice.channel
    voice = ctx.voice_client

    if voice is None and subcommand != "play":
        await ctx.send("Bot is not playing anything")
        return

    try:
        match subcommand:
            case "play":
                try:
                    voice = await voice_channel.connect()
                except discord.ClientException:
                    pass

                res = pytubefix.Search(query).videos[0]

                await ctx.send(
                    f"The search '{query}' gave the following result"
                    f"```{res.title}```"
                    "The title will be added to the queue"
                )

                add_to_queue(res)

                if len(song_queue) == 1:
                    await move_queue(ctx, remove=False)
            case "stop":
                song_queue = []
                await voice.disconnect()
                delete_all_downloaded_songs()
            case "skip":
                voice.stop()
            case "pause":
                await ctx.send("Paused")
                voice.pause()
            case "resume":
                await ctx.send("Resumed")
                voice.resume()
            case "queue":
                if not len(song_queue):
                    await ctx.send("Queue is empty")
                    return

                queue_string = f"```{QUEUE_TEXT}"

                queue_string += f"Now playing: {song_queue[0][0].title}\n\n"
                for idx, (song, _) in enumerate(song_queue):
                    if idx == 0:
                        continue

                    queue_string += f"{idx:11}: {song.title}\n"
                queue_string += "```"
                await ctx.send(queue_string)
    except Exception as e:
        await call_admin(ctx, e)


async def move_queue(ctx: commands.Context, remove=True):
    global song_queue
    if ctx.voice_client is None:
        song_queue = []
        return

    refresh_downloads()

    if remove:
        song, song_id = song_queue[0]
        song_path = (
            root_path / "resources" / "downloaded_songs" / f"{song_id}.mp4"
        )
        print(f"Song {song.title} has ended, deleting file {song_path}")
        os.remove(song_path)
        song_queue = song_queue[1:]

    if len(song_queue):
        song, song_id = song_queue[0]
        await ctx.send(f"Currently playing\n{song.watch_url}")
        song_path = (
            root_path / "resources" / "downloaded_songs" / f"{song_id}.mp4"
        )
        while not os.path.exists(song_path):
            print(f"Waiting for {song.title} to be downloaded...")
            await asyncio.sleep(1)
        ctx.voice_client.play(
            discord.FFmpegPCMAudio(song_path),
            after=lambda x: client.loop.create_task(move_queue(ctx)),
        )

    else:
        await ctx.send("Queue has reached its end, see you soon :D")
        await ctx.voice_client.disconnect()
        delete_all_downloaded_songs()

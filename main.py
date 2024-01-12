import discord
from dotenv import load_dotenv
from os import environ as env
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import json
import glob
import os

bot = discord.Bot()
connections = {}
load_dotenv()

deepgram = DeepgramClient(env.get("DEEPGRAM_API_TOKEN"))

options = PrerecordedOptions(
    model="nova",
    smart_format=True,
    utterances=True,
    punctuate=True,
    diarize=True,
    detect_language=True
)

discord.opus.load_opus(
    "/usr/local/opt/opus/lib/libopus.0.dylib"
)  # Load the opus library.

@bot.command()
async def record(ctx):  # If you're using commands.Bot, this will also work.
    voice = ctx.author.voice

    if not voice:
        await ctx.respond("You aren't in a voice channel!")

    vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
    connections.update(
        {ctx.guild.id: vc}
    )  # Updating the cache with the guild and channel.

    vc.start_recording(
        discord.sinks.WaveSink(),  # The sink type to use.
        once_done,  # What to do once done.
        ctx.channel,  # The channel to disconnect from.
    )
    await ctx.respond("Started recording!")


async def once_done(
    sink: discord.sinks, channel: discord.TextChannel, *args
):  # Our voice client already passes these in.
    recorded_users = [  # A list of recorded users
        f"<@{user_id}>" for user_id, audio in sink.audio_data.items()
    ]
    await sink.vc.disconnect()  # Disconnect from the voice channel.

    words = []

    # save the file to disk
    for user_id, audio in sink.audio_data.items():
        payload: FileSource = {
            "buffer": audio.file.read(),
        }

        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

        words = response['results']['channels'][0]['alternatives'][0]['words']

        # add the speaker to the words
        for word in words: 
            word = word.to_dict()
            word.speaker = user_id
            words.append(word)

    # sort the words by start time
    words.sort(key=lambda x: x['start'])

    print(words)

    await channel.send(
        f"finished recording audio for: {', '.join(recorded_users)}."
    )  # Send a message with the accumulated files.


@bot.command()
async def stop_recording(ctx):
    if ctx.guild.id in connections:  # Check if the guild is in the cache.
        vc = connections[ctx.guild.id]
        vc.stop_recording()  # Stop recording, and call the callback (once_done).
        del connections[ctx.guild.id]  # Remove the guild from the cache.
        await ctx.delete()  # And delete.
    else:
        await ctx.respond(
            "I am currently not recording here."
        )  # Respond with this if we aren't recording.


bot.run(env.get("DISCORD_BOT_TOKEN"))

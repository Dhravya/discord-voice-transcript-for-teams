import discord
import openai
from dotenv import load_dotenv
from os import environ as env
from const import conversationSummarySchema
from deepgram import DeepgramClient, PrerecordedOptions, FileSource

bot = discord.Bot()
connections = {}
load_dotenv()

deepgram = DeepgramClient(env.get("DEEPGRAM_API_TOKEN"))

options = PrerecordedOptions(
    model="nova-2",
    smart_format=True,
    utterances=True,
    punctuate=True,
    diarize=True,
    detect_language=True,
)

discord.opus.load_opus("/usr/local/opt/opus/lib/libopus.0.dylib")

client = openai.OpenAI(
    base_url="https://api.endpoints.anyscale.com/v1",
    api_key=env.get("ANYSCALE_MISTRAL_TOKEN"),
)


@bot.command()
async def record(ctx):
    voice = ctx.author.voice

    if not voice:
        await ctx.respond("⚠️ You aren't in a voice channel!")

    vc = await voice.channel.connect()
    connections.update({ctx.guild.id: vc})

    vc.start_recording(
        discord.sinks.WaveSink(),
        once_done,
        ctx.channel,
    )
    await ctx.respond("🔴 Listening to this conversation.")


async def once_done(sink: discord.sinks, channel: discord.TextChannel, *args):
    recorded_users = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
    await sink.vc.disconnect()

    words_list = []

    for user_id, audio in sink.audio_data.items():
        payload: FileSource = {
            "buffer": audio.file.read(),
        }

        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

        words = response["results"]["channels"][0]["alternatives"][0]["words"]

        words = [word.to_dict() for word in words]

        for word in words:
            # if speaker is not 0, then it's someone else, set the user ID to that.
            ## This is to make sure that the dearize work. if multiple people are speaking from the same user ID
            if word["speaker"] != 0:
                user_id = word["speaker"]

            new_word = {
                "word": word["word"],
                "start": word["start"],
                "end": word["end"],
                "confidence": word["confidence"],
                "punctuated_word": word["punctuated_word"],
                "speaker": user_id,
                "speaker_confidence": word["speaker_confidence"],
            }
            words_list.append(new_word)

    words_list.sort(key=lambda x: x["start"])

    print(words_list)

    transcript = ""
    current_speaker = None

    for word in words_list:
        if "speaker" in word and word["speaker"] != current_speaker:
            transcript += f"\n\nSpeaker <@{word['speaker']}>: "
            current_speaker = word["speaker"]
        transcript += f"{word['punctuated_word']} "

    transcript = transcript.strip()

    chat_completion = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        messages=[
            {
                "role": "system",
                "content": "You are a conversation summarizer. You are also responsible to assign action items to the users. Below is a transcript of a conversation",
            },
            {"role": "user", "content": transcript},
        ],
        temperature=0.7,
        tools=[{"type": "function", "function": conversationSummarySchema}],
    )

    await channel.send(
        f"finished recording audio for: {', '.join(recorded_users)}. Here is the transcript: \n\n{transcript}\n\nHere is the summary: \n\n{chat_completion.choices[0].message.content}"
    )


@bot.command()
async def stop_recording(ctx):
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_recording()
        del connections[ctx.guild.id]
        await ctx.delete()
    else:
        await ctx.respond("🚫 Not recording here")


bot.run(env.get("DISCORD_BOT_TOKEN"))

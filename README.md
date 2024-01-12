### A Discord Bot that listens to a voice channel, transcribes the audio and assigns tasks to the users.

Working in startups and small teams on discord, I often found myself in the situation where I had to take notes during a meeting. This is possible on google meet and other services using otter.ai, fireflies.ai and other services. But there's nothing for discord.

## How to use

1. Create a discord bot and invite it to your server. [Guide](https://discordpy.readthedocs.io/en/latest/discord.html)
2. Clone this repo and install the requirements `pip install -r requirements.txt`
3. Create a `.env` file and add the following variables:
    - `DISCORD_BOT_TOKEN`: The token of your discord bot
    - `DEEPGRAM_API_TOKEN`: For transcription
    - `ANYSCALE_MISTRAL_TOKEN`: For summary and analysis of the transcript

4. Run the bot `python main.py`

## Commands

- `/record` - Starts recording the audio in the voice channel
- `/stop_recording` - Stops recording the audio in the voice channel

## Tools used

- [Deepgram](https://www.deepgram.com/) - For transcription
- [Anyscale](https://www.anyscale.com/) - For summary and analysis of the transcript, used because it allows function calling on mistral.
- [Pycord](https://pycord.dev) - Python wrapper for discord api
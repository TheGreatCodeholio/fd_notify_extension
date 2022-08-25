import discord
import asyncio
import datetime
from threading import Thread
import time
import etc.config as config
from quart import Quart, request

app = Quart(__name__)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
voice_client = None
queue_total = 0


# Setup for Discord bot
@app.before_serving
async def before_serving():
    loop = asyncio.get_event_loop()
    await client.login(config.discord_settings["discord_bot_token"])
    loop.create_task(client.connect())


# Setup for webhook to receive POST and send it to Discord bot
@app.route('/voice', methods=['POST'])
async def voice_post():
    global voice_client, queue_total
    if request.is_json:
        data = await request.get_json()
        if "call_mp3_path" in data:
            call_mp3_path = data["call_mp3_path"]
        else:
            return 'no path given', 403
        if queue_total >= 3:
            return 'queue full', 666
        if voice_client is None:
            vc = client.get_channel(config.discord_settings["discord_voice_channel"])
            voice_client = await vc.connect()
        if not voice_client.is_playing():
            voice_client.play(discord.FFmpegPCMAudio(call_mp3_path))
            return 'playing', 200
        else:
            queue_total += 1
            Thread(target=queue_loop, args=(call_mp3_path, queue_total)).start()
            return 'queued for next play', 200

    else:
        return 'Failed - Not a JSON', 403


@app.route('/text', methods=['POST'])
async def text_post():
    if request.is_json:
        data = await request.get_json()
        timestamp = datetime.datetime.fromtimestamp(data["timestamp"])
        embed = discord.Embed(title="🚨 Dispatch Alert 🚨", description="Click for Dispatch Audio",
                              colour=discord.Colour(0xcb151e), url=f'{data["mp3_url"]}')
        embed.add_field(name=f"Time: ",
                        value=f'{timestamp.strftime("%H")}:{timestamp.strftime("%M")} {timestamp.strftime("%b %d %Y")}')
        if data["detector_name"] == "multi":
            detectors = ""
            for det in data["detectors"]:
                detectors += str(data["detectors"][det])
            embed.add_field(name=f"Departments:", value=detectors)
        else:
            embed.add_field(name=f"Department:", value=data["detector_name"])
        text_channel = client.get_channel(config.discord_settings["discord_text_channel"])
        await text_channel.send(embed=embed)
        return 'Posted', 200
    else:
        return 'Failed', 403


@app.route('/noaa', methods=['POST'])
async def noaa_text_post():
    if request.is_json:
        alert_data = await request.get_json()
        embed = discord.Embed(title="⚠️ Weather Alert ⚠️", description="Click for Detailed Summary",
                              colour=discord.Colour(0xcb151e), url=f'{config.base_url + "/wx_summary.php"}')
        embed.add_field(name=f'Type', value=f'{alert_data["event"]}', inline=False)
        embed.add_field(name=f'Urgency', value=f'{alert_data["urgency"]}', inline=False)
        embed.add_field(name=f'Certainty', value=f'{alert_data["certainty"]}', inline=False)
        embed.add_field(name=f'Expires', value=f'{alert_data["expires_hrt"]}', inline=False)
        embed.add_field(name=f'Link', value=f'{config.base_url + "/wx_summary.php"}', inline=False)
        embed.add_field(name=f'Summary', value=f'{alert_data["summary"]}', inline=False)
        text_channel = client.get_channel(config.discord_settings["discord_text_channel"])
        await text_channel.send(embed=embed)
        return 'Posted', 200
    else:
        return 'Failed', 403


# Setup for webhook to receive POST and send it to Discord bot
@app.route('/', methods=['GET'])
async def index():
    global queue_total
    data = {"calls_queued": queue_total}
    return data


def queue_loop(audio_file_path, queue_number):
    global voice_client, queue_total
    while voice_client.is_playing():
        print("I am " + str(queue_number) + " in queue")
        time.sleep(2)
    queue_total -= 1
    voice_client.play(discord.FFmpegPCMAudio(audio_file_path))


if __name__ == '__main__':
    app.run()

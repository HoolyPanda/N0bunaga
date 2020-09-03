import os
import ffmpeg
import youtube_dl
import discord
from discord.ext import commands

token = open(f'./token.cred').readline()
testUrl = f'https://www.youtube.com/watch?v=02Tim9kmb3I'
testId = 698604865634435202
tortUrl = f'https://www.youtube.com/watch?v=pBqyntzYaoQ'

# a = os.getcwd()
yt_dlOpts = {
    'format': 'bestaudio/mp3',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': f'{os.getcwd()}/downloads/%(title)s.%(ext)s'
}
print(os.getcwd())
   

# client = discord.Client()
client: commands.Bot
client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    print(f'{client.user}')

@client.command()
async def ping(context):
    await context.send(f'Pong')

def __PlayAudio(vClient:discord.VoiceClient):
    path = f'{os.getcwd()}/downloads'
    for f in os.listdir(path):
        if f.split('.')[-1] == 'mp3':
            audioS = discord.FFmpegPCMAudio(f'{path}/{f}')
            vClient.play(audioS)
            b = 0

@client.command(pass_context=True)
async def play(context:commands.context, url):
    ytDl =  youtube_dl.YoutubeDL()
    with youtube_dl.YoutubeDL(yt_dlOpts ) as ydl:
        # ydl.download([testUrl]) 
        voiceClient: discord.VoiceClient
        voiceChannel = client.get_channel(context.message.author.voice.channel.id)
        voiceClient = await voiceChannel.connect()
        __PlayAudio(voiceClient)
    await voiceClient.disconnect()
    pass

@client.command(pass_context=True)
async def torture(context:commands.context, name):
    n = name
    # context.
    print(n)
    for memebr in context.guild.members:
        if memebr.mention == n:
            for c in context.guild.channels:
                if c.id == testId:
                    await memebr.move_to(c)
                    voiceClient = await client.get_channel(testId).connect()
                    ytDl =  youtube_dl.YoutubeDL()
                    with youtube_dl.YoutubeDL(yt_dlOpts) as ydl:
                        # ydl.download([tortUrl]) 
                        __PlayAudio(voiceClient)
            # await voiceClient.disconnect()
            z = 0
    a = 0

client.run(token)


# client.connect()
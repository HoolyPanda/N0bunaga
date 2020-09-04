import os
import youtube_dl
import discord
from threading import Thread
from discord.ext import commands
from musicPlayer import MusicPlayer
import requests
import bs4

token = open(f'./token.cred').readline()
testUrl = f'https://www.youtube.com/watch?v=02Tim9kmb3I'
testId = 698604865634435202
tortUrl = f'https://www.youtube.com/watch?v=pBqyntzYaoQ'

playMusic = False
currentTrack = ''
musicFolder = f'{os.getcwd()}/downloads'
__musicPlayer: Thread
mP: MusicPlayer
mP = None
musicQueue = []
domain = 'live'


print(os.getcwd())

client: commands.Bot
client = commands.Bot(command_prefix='self.')


@client.event
async def on_ready():
    print(f'{client.user}')

@client.command()
async def ping(context):
    await context.send(f'Pong')

@client.command(pass_context=True)
async def download(context:commands.context, url):
    id = len(os.listdir(musicFolder))
    yt_dlOpts = {'format': 'bestaudio/mp3','outtmpl': f'{os.getcwd()}/downloads/{id}.%(title)s.%(ext)s'}
    with youtube_dl.YoutubeDL(yt_dlOpts) as ydl:
        ydl.download([url]) 
    pass

@client.command(pass_context=True)
async def play(context:commands.context):
    voiceChannel = client.get_channel(context.message.author.voice.channel.id)
    vc = await voiceChannel.connect()
    global mP
    mP = MusicPlayer(vc)
    mP.play()

@client.command(pass_context=True)
async def pause(context: commands.context):
    if mP:
        mP.pause()

@client.command(pass_context=True)
async def resume(context: commands.context):
    mP.resume()

@client.command(pass_context=True)
async def stop(context: commands.context):
    mP.stop()

@client.command(pass_context=True)
async def next(context: commands.context):
    mP.next()

@client.command(pass_context=True)
async def clear(context: commands.context):
    mP.clearQueue()

@client.command(pass_context=True)
async def ls(context: commands.context):
    msg = ''
    if mP is None:
        await context.channel.send(content=f'Очередь пуста')
    else:
        if len(mP.queue) == 0:
            await context.channel.send(content=f'Очередь пуста')
        else:
            for i in mP.queue:
                msg += f'{i}\n'
            await context.channel.send(content=str(msg))

@client.command(pass_context=True)
async def manga(context: commands.context):
    domain = 'live'
    req = requests.get(f'https://readmanga.{domain}/internal/random')
    await context.channel.send(content= req.url)

@client.command(pass_context=True)
async def get_boobs(context: commands.context):
    req = requests.get(f'https://tits-guru.com/randomTits')
    # parsedReq = 
    # await context.channel.send(content= req.url)
    
@client.command(pass_context=True)
async def set_domain(context: commands.context, dmn):
    domain = dmn
    await context.channel.send(content= f'https://readmanga.{domain}')
    

@client.command(pass_context=True)
async def torture(context:commands.context, name):
    n = name
    print(n)
    for memebr in context.guild.members:
        if memebr.mention == n:
            for c in context.guild.channels:
                if c.id == testId:
                    global mP
                    if not mP is None:
                        mP.clearQueue()
                    await download(context, tortUrl)
                    await memebr.move_to(c)
                    voiceClient = await client.get_channel(testId).connect()
                    mP = MusicPlayer(voiceClient)
                    mP.play()

client.run(token)
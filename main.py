import os
import youtube_dl
import discord
from threading import Thread
from discord.ext import commands
from musicPlayer import MusicPlayer
import requests
import yandex_music
from yandex_music import Client
from threading import Thread
import bs4
import re


token = open(f'./token.cred').readline()
testUrl = f'https://www.youtube.com/watch?v=02Tim9kmb3I'
testId = 698604865634435202
tortUrl = f'https://www.youtube.com/watch?v=pBqyntzYaoQ'

playMusic = False
# currentTrack = ''
musicFolder = f'{os.getcwd()}/downloads'
__musicPlayer: Thread
mP: MusicPlayer
mP = MusicPlayer(None)
musicQueue = []
mangaDomain = 'live'
animeDomain = 'net'

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
    if 'https://music.yandex.ru' in url:
        clnt= captcha_key = captcha_answer = None
        while not clnt:
            try:
                clnt = Client.from_credentials(open('./login.cred').readline(), open('./password.cred').readline(), captcha_answer, captcha_key)
            except yandex_music.exceptions.Captcha as e:
                e.captcha.download('captcha.png')
                captcha_key = e.captcha.x_captcha_key
                captcha_answer = input('Число с картинки: ')
        if 'track' in url:
            await context.channel.send(content= f'Processing tack') 
            tr = re.findall('\d+', f'{url}')
            track = clnt.tracks([tr[1]])[0]
            def test():
                clnt.tracks([tr[1]])[0].download(f'{musicFolder}/{id}.{track.title}.mp3')
            Thread(target=test).start()
            mP.updateQueue()
            await context.channel.send(content= f'track ready')
            pass
        else: 
            album = re.findall('\d+', f'{url}')
            album = clnt.albumsWithTracks(album[0])
            await context.channel.send(content= f'Processing album {album.title}')
            def test():
                for volume in album.volumes:
                    for track in volume:
                        id = len(os.listdir(musicFolder))
                        track.download(f'{musicFolder}/{id}.{track.title}.mp3')
            t = Thread(target=test)
            t.start()
            t.join()
            mP.updateQueue()
            await context.channel.send(content= f'Album ready')
        pass
    else:
        yt_dlOpts = {'format': 'bestaudio/mp3',
                'audio-quality': '9',
                'audio-format': 'mp3',
                'outtmpl': f'{os.getcwd()}/downloads/{id}.%(title)s.%(ext)s'
                }
        with youtube_dl.YoutubeDL(yt_dlOpts) as ydl:
            await context.channel.send(content= f'Processing tack') 
            def test():
                ydl.download([url])
            t = Thread(target=test)
            t.start()
            t.join()
            mP.updateQueue()
            await context.channel.send(content= f'track ready')
        pass

@client.command(pass_context=True)
async def play(context:commands.context):
    voiceChannel = client.get_channel(context.message.author.voice.channel.id)
    try:
        vc = await voiceChannel.connect()
        global mP
        mP.voiceClient = vc
    except Exception as e:
        pass
    mP.updateQueue()
    if not mP.play():
        mP.updateQueue()
        await context.channel.send(content=f'Больше нет треков')

@client.command(pass_context=True)
async def currentTrack(context: commands.context):
    try:
        await context.channel.send(content=f'Current track is {mP.currentTrack}')
    except Exception as e:
        await context.channel.send(content=f'Cannot define current track')

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
    await mP.voiceClient.disconnect()

@client.command(pass_context=True)
async def next(context: commands.context):
    if not mP.next():
        mP.clearQueue()
        mP.updateQueue()
        await context.channel.send(content=f'Больше нет треков')

@client.command(pass_context=True)
async def clear(context: commands.context):
    mP.clearQueue()

@client.command(pass_context=True)
async def ls(context: commands.context):
    msg = ''
    if mP is None:
        await context.channel.send(content=f'Очередь пуста')
    else:
        mP.updateQueue()
        if len(mP.queue) == 0:
            await context.channel.send(content=f'Очередь пуста')
        else:
            for i in mP.queue:
                msg += f'{i}\n'
            await context.channel.send(content=str(msg))

@client.command(pass_context=True)
async def manga(context: commands.context):
    # mangaDomain = 'live'
    req = requests.get(f'https://readmanga.{mangaDomain}/internal/random')
    await context.channel.send(content= req.url)

@client.command(pass_context=True)
async def anime(context: commands.context):
    req = requests.get(f'https://findanime.{animeDomain}/internal/random')
    await context.channel.send(content= req.url)

@client.command(pass_context=True)
async def get_boobs(context: commands.context):
    req = requests.get(f'https://tits-guru.com/randomTits')

@client.command(pass_context=True)
async def setMangaDomain(context: commands.context, dmn):
    global mangaDomain
    mangaDomain = dmn
    await context.channel.send(content= f'https://readmanga.{mangaDomain}')

@client.command(pass_context=True)
async def setAnimeDomain(context: commands.context, dmn):
    global animeDomain
    animeDomain = dmn
    await context.channel.send(content= f'https://findanime.{animeDomain}')

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
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


token = open(f'./token.cred').readline().replace("\n","")
testUrl = f'https://www.youtube.com/watch?v=02Tim9kmb3I'
testId = 698604865634435202
tortUrl = f'https://www.youtube.com/watch?v=fp7ZG5j0VJA'

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
client = commands.Bot(command_prefix='.')

@client.event
async def on_ready():
    print(f'{client.user}')

@client.command()
async def ping(context):
    """
    test
    """
    await context.send(f'Pong')

@client.command(pass_context=True)
async def help_command(context:commands.context):
    msg =""" 
    .d <URL> - скачивает на сервер трек\альбом с яндекс музыки или ютуба
    .p - начинает воспроизведение
    .n - начинает воспроизведение следующего трека 
    .s - останавливает воспроизведение
    .ls - выводит всю очередь треков
    .cl - очищает всю очередь
    .anime - отправляет ссылку на случайное аниме
    .manga - отправляет ссылку на случайную мангу
    .setAnimeDomain <domain> - (сервисная) меняет домен у сайта для аниме
    .setMangaDomain <domain> - (сервисная) меняет домен у сайта для манги
    .t <user> - (сервисная) отправляет ползователя в пыточную и там пытает
    """
    # await context.au
    await context.channel.send(content= f'{msg}')
@client.command(pass_context=True)
async def d(context:commands.context, url):
    '''
    .d <URL> - скачивает на сервер трек\альбом с яндекс музыки или ютуба
    '''
    id = len(os.listdir(musicFolder))
    if 'https://music.yandex.ru' in url:
        clnt= captcha_key = captcha_answer = None
        while not clnt:
            try:
                clnt = Client.from_credentials(open('./login.cred').readline().replace("\n",""), open('./password.cred').readline().replace("\n",""), captcha_answer, captcha_key)
            except yandex_music.exceptions.Captcha as e:
                e.captcha.download('captcha.png')
                captcha_key = e.captcha.x_captcha_key
                captcha_answer = input('Число с картинки: ')
        if 'track' in url:
            await context.channel.send(content= f'Processing tack') 
            tr = re.findall('\d+', f'{url}')
            track = clnt.tracks([tr[1]])[0]
            artist = track.artists[0].name

            def test():
                clnt.tracks([tr[1]])[0].download(f'{musicFolder}/{id}.{track.title} by {artist}.mp3')
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
async def q(context:commands.context):
    pass
@client.command(pass_context=True)
async def p(context:commands.context):
    '''
    .p - начинает воспроизведение
    '''
    voiceChannel = client.get_channel(context.message.author.voice.channel.id)
    try:
        vc = await voiceChannel.connect()
        global mP
        mP.voiceClient = vc
    except Exception as e:
        print(e)
        pass
    mP.updateQueue()
    await mP.play()

@client.command(pass_context=True)
async def ct(context: commands.context):
    '''
    '''
    try:
        await context.channel.send(content=f'Current track is {mP.currentTrack}')
    except Exception as e:
        await context.channel.send(content=f'Cannot define current track')

@client.command(pass_context=True)
async def pause(context: commands.context):
    '''
    '''
    if mP:
        mP.pause()

@client.command(pass_context=True)
async def resume(context: commands.context):
    '''
    '''
    mP.resume()

@client.command(pass_context=True)
async def s(context: commands.context):
    '''
    self.stop - останавливает воспроизведение
    '''
    await mP.stop()

@client.command(pass_context=True)
async def n(context: commands.context):
    '''
    self.next - начинает воспроизведение следующего трека 
    '''
    if not await mP.next():
        mP.clearQueue()
        mP.updateQueue()
        await context.channel.send(content=f'Больше нет треков')
        await mP.voiceClient.disconnect()

@client.command(pass_context=True)
async def cl(context: commands.context):
    '''
    self.clear - очищает всю очередь
    '''
    mP.clearQueue()

@client.command(pass_context=True)
async def ls(context: commands.context):
    '''
    self.ls - выводит всю очередь треков
    '''
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
    '''
    self.manga - отправляет ссылку на случайную мангу
    '''
    # mangaDomain = 'live'
    req = requests.get(f'https://readmanga.{mangaDomain}/internal/random')
    await context.channel.send(content= req.url)

@client.command(pass_context=True)
async def anime(context: commands.context):
    '''
    self.anime - отправляет ссылку на случайное аниме
    '''
    req = requests.get(f'https://findanime.{animeDomain}/internal/random')
    await context.channel.send(content= req.url)

# @client.command(pass_context=True)
async def get_boobs(context: commands.context):
    req = requests.get(f'https://tits-guru.com/randomTits')

@client.command(pass_context=True)
async def setMangaDomain(context: commands.context, dmn):
    '''
    self.setMangaDomain <domain> - (сервисная) меняет домен у сайта для манги
    '''
    global mangaDomain
    mangaDomain = dmn
    await context.channel.send(content= f'https://readmanga.{mangaDomain}')

@client.command(pass_context=True)
async def setAnimeDomain(context: commands.context, dmn):
    '''
    self.setAnimeDomain <domain> - (сервисная) меняет домен у сайта для аниме
    '''
    global animeDomain
    animeDomain = dmn
    await context.channel.send(content= f'https://findanime.{animeDomain}')

@client.command(pass_context=True)
async def t(context:commands.context, name):
    '''
    self.torture <user> - (сервисная) отправляет ползователя в пыточную и там пытает
    '''
    n = name
    print(n)
    for memebr in context.guild.members:
        if memebr.mention == n:
            for c in context.guild.channels:
                if c.id == testId:
                    global mP
                    if not mP is None:
                        mP.clearQueue()
                    else:
                        await d(context, tortUrl)
                        await memebr.move_to(c)
                        voiceClient = await client.get_channel(testId).connect()
                        mP = MusicPlayer(voiceClient)
                        await mP.play()

client.run(token)

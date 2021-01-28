import discord
import os
from threading import Thread
from multiprocessing import Process
import yandex_music
import asyncio

# discord.VoiceClient.disconnect

class MusicPlayer():
    def __init__(self, voiceClient: discord.VoiceClient):
        self.voiceClient = voiceClient
        self.currentTrack = ''
        self.currentAudioSource = None
        self.musicFolder = f'{os.getcwd()}/downloads'
        self.queueBlacklist = []
        self.queue = self.updateQueue()
        self.queueThread: Thread
        self.isPaused = False
        self.stopPlaying = False
        self.queuePosition = -1
    
    def _setUpTrack(self):
        self.currentTrack = self.queue[self.queuePosition]
        self.currentAudioSource = discord.FFmpegPCMAudio(f'{self.musicFolder}/{self.currentTrack}')
        if not self.voiceClient.is_playing():
            self.voiceClient.play(self.currentAudioSource)


    async def __PlayQueue(self):
        while len(self.queue) > self.queuePosition and not self.stopPlaying:
            self.queue = self.updateQueue()
            self.updateQueue()
            if not self.voiceClient.is_playing() and not self.isPaused:
                try:
                    self.queuePosition += 1
                    if len(self.queue) > 0:
                        self.currentTrack = self.queue[self.queuePosition]
                        self.currentAudioSource = discord.FFmpegPCMAudio(f'{self.musicFolder}/{self.currentTrack}')
                        if not self.voiceClient.is_playing():
                            self.voiceClient.play(self.currentAudioSource)
                except Exception as e:
                    break

    async def CheckQueue(self):
        self.updateQueue()
        if len(self.queue) > self.queuePosition:
            self.currentTrack = self.queue[self.queuePosition]
            self.currentAudioSource = discord.FFmpegPCMAudio(f'{self.musicFolder}/{self.currentTrack}')
            return await self.play_next()

    def get_next_track(self):
        self.updateQueue()
        self.voiceClient.stop()
        if len(self.queue) > self.queuePosition:
            self.currentTrack = self.queue[self.queuePosition]
            self.currentAudioSource = discord.FFmpegPCMAudio(f'{self.musicFolder}/{self.currentTrack}')
            if len(self.queue) -1>= self.queuePosition:
                if self.voiceClient is None: print("VC NONE")
                try:
                    self.queuePosition += 1
                    if len(self.queue) <= self.queuePosition:
                        self.clearQueue()
                        self.voiceClient.stop()
                        # self.quit()
                    else:
                        self.currentTrack = self.queue[self.queuePosition]
                        self.currentAudioSource = discord.FFmpegPCMAudio(f'{self.musicFolder}/{self.currentTrack}')
                        self.voiceClient.play(self.currentAudioSource, after= lambda x: self.get_next_track())
                except Exception as e:
                    print(e)
                    pass


    async def play_next(self):
        if len(self.queue) -1>= self.queuePosition and not self.stopPlaying:
            self.queue = self.updateQueue()
            self.updateQueue()
            if self.voiceClient is None: print("VC NONE")
            try:
                self.queuePosition += 1
                if len(self.queue) <= self.queuePosition:
                    self.clearQueue()
                    self.voiceClient.stop()

                    # await self.voiceClient.disconnect()
                    # await self.quit()
                    return False
                else:
                    try:
                        await self.stop()
                    except: pass
                    self.currentTrack = self.queue[self.queuePosition]
                    self.currentAudioSource = discord.FFmpegPCMAudio(f'{self.musicFolder}/{self.currentTrack}')
                    self.voiceClient.play(self.currentAudioSource, after= lambda x: self.get_next_track())
                    return True
            except Exception as e:
                print(e)
                pass
        elif self.stopPlaying: return True 

    async def play(self):
        self.stopPlaying = self.isPaused = False
        return await self.CheckQueue()

    def pause(self):
        self.isPaused = True
        self.voiceClient.pause()
    
    def resume(self):
        self.voiceClient.play(self.currentAudioSource)
        self.isPaused = False
    
    async def stop(self):
        self.stopPlaying = True
        await self.voiceClient.stop()
        # await self.voiceClient.disconnect()
        self.currentTrack = ''

    async def quit(self):
        self.stopPlaying = True
        await self.clearQueue()
        await self.voiceClient.disconnect()


    def clearQueue(self):
        for t in self.queue:
            os.remove(f'{self.musicFolder}/{t}')
        self.queue = []
        self.currentAudioSource = None
        self.currentTrack = ''
        self.queuePosition = -1

    def updateQueue(self):
        def _sortKey(arg):
            a = int(arg.split('.')[0])
            return int(arg.split('.')[0])
        self.queue = []
        # self.queuePosition = 0
        self.queue = os.listdir(self.musicFolder)
        self.queue.sort(key=_sortKey)
        return self.queue

    def deleteTrack(self, id):


        pass

    async def next(self):
        await self.stop()
        self.updateQueue()
        return await self.play()
        # self.queue.pop(0)
        # self.queuePosition += 1
        # return self.play_next()

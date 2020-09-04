import discord
import os
from threading import Thread

class MusicPlayer():
    def __init__(self, voiceClient: discord.VoiceClient):
        self.voiceClient = voiceClient
        self.currentTrack = ''
        self.currentAudioSource = None
        self.musicFolder = f'{os.getcwd()}/downloads'
        self.queueBlacklist = []
        self.queue = os.listdir(self.musicFolder)
        self.queueThread: Thread
        self.isPaused = False
        self.stopPlaying = False
    
    def __PlayQueue(self):
        while len(self.queue) > 0 and not self.stopPlaying:
            if not self.voiceClient.is_playing() and not self.isPaused:
                try:
                    self.queue.pop(0)
                    os.remove(f'{self.musicFolder}/{self.currentTrack}')
                    if len(self.queue) > 0:
                        self.currentTrack = self.queue[0]
                        self.currentAudioSource = discord.FFmpegPCMAudio(f'{self.musicFolder}/{self.currentTrack}')
                        if not self.voiceClient.is_playing():
                            self.voiceClient.play(self.currentAudioSource)
                except Exception as e:
                    break

    def play(self):
        if len(self.queue) > 0:
            self.currentTrack = self.queue[0]
            self.currentAudioSource = discord.FFmpegPCMAudio(f'{self.musicFolder}/{self.currentTrack}')
            if not self.voiceClient.is_playing():
                self.voiceClient.play(self.currentAudioSource)
                self.queueThread = Thread(target=self.__PlayQueue)
                self.queueThread.start()

    def pause(self):
        self.isPaused = True
        self.voiceClient.pause()
    
    def resume(self):
        self.voiceClient.play(self.currentAudioSource)
        self.isPaused = False
    
    async def stop(self):
        self.stopPlaying = True
        self.isPaused = True
        self.voiceClient.stop()
        self.currentTrack = ''
        self.stopPlaying = False
        self.isPaused = False
        await self.voiceClient.disconnect()

    def clearQueue(self):
        self.stop()
        for t in self.queue:
            os.remove(f'{self.musicFolder}/{t}')
        self.queue = []
        self.currentAudioSource = None
        self.currentTrack = ''

    def updateQueue(self):
        self.queue = []
        pass

    def deleteTrack(self, id):


        pass

    def next(self):
        self.stop()
        self.queue.pop(0)
        self.play()

import discord
import os
from threading import Thread
import yandex_music

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
        self.queuePosition = 0
    
    def __PlayQueue(self):
        while len(self.queue) > self.queuePosition and not self.stopPlaying:
            self.queue = os.listdir(self.musicFolder)
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

    def play(self):
        self.stopPlaying = False
        self.isPaused = False
        self.queue = os.listdir(self.musicFolder)
        if len(self.queue) > self.queuePosition:
            self.currentTrack = self.queue[self.queuePosition]
            self.currentAudioSource = discord.FFmpegPCMAudio(f'{self.musicFolder}/{self.currentTrack}')
            if not self.voiceClient.is_playing():
                self.voiceClient.play(self.currentAudioSource)
                self.queueThread = Thread(target=self.__PlayQueue)
                self.queueThread.start()
                return True
        else:
            return False

    def pause(self):
        self.isPaused = True
        self.voiceClient.pause()
    
    def resume(self):
        self.voiceClient.play(self.currentAudioSource)
        self.isPaused = False
    
    def stop(self):
        self.stopPlaying = True
        self.isPaused = True
        self.voiceClient.stop()
        self.currentTrack = ''

    def clearQueue(self):
        try:
            self.stop()
        except Exception as e:
            pass
        for t in self.queue:
            os.remove(f'{self.musicFolder}/{t}')
        self.queue = []
        self.currentAudioSource = None
        self.currentTrack = ''
        self.queuePosition = 0

    def updateQueue(self):
        self.queue = []
        # self.queuePosition = 0
        self.queue = os.listdir(self.musicFolder)
        pass

    def deleteTrack(self, id):


        pass

    def next(self):
        self.stop()
        self.updateQueue()
        # self.queue.pop(0)
        self.queuePosition += 1
        return self.play()

#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2009 Edmundo Carmona Antoranz

# Released under the terms of the Affero GPLv3

import sys
from Wave import Wave
import os
from threading import Thread
from time import *

class WavePlayer:

    def __init__(self, samplingRate = 44100, outputStream = None, debug = False):
        self.samplingRate = samplingRate
        self.volume=1
        self.debug = debug
        self.outputStream = outputStream
        self.pcm = None

        if outputStream == None:
            if debug:
                sys.stderr.write("Trying to open sound output\n")
            if os.name == 'posix':
                if debug:
                    sys.stderr.write("Trying to access alsa\n")
                import alsaaudio
                self.pcm = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL)
                self.pcm.setrate(samplingRate)
                self.pcm.setperiodsize(samplingRate / 5)
                self.pcm.setchannels(2)
                self.pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
                self.pcmBuffer = ""
                self.alsaHandler = AlsaHandler(self.pcm)
            else:
                print("Unknown OS: " + os.name

    def setVolume(self, volume):
        if volume > 1:
            self.volume=1
        elif volume < 0:
            self.volume = 0
        else:
            self.volume=volume

    def play(self, leftChannel, rightChannel = None):
        leftChannel *= int(self.volume)
        if rightChannel != None:
            rightChannel *= int(self.volume)
        else:
            rightChannel = leftChannel

        if self.debug:
            sys.stderr.write("Left: " + str(leftChannel) + " Right: " + str(rightChannel) + "\n")

        if leftChannel < 0:
            leftChannel = leftChannel ^ 0xffff + 1
        if rightChannel < 0:
            rightChannel = rightChannel ^ 0xffff + 1

        if self.outputStream == None:
            # PCM
            self.pcmBuffer += "%(c1)c%(c2)c%(c3)c%(c4)c" % {'c1' : leftChannel & 0xff, 'c2' : leftChannel >> 8 & 0xff, 'c3' : rightChannel & 0xff, 'c4' : rightChannel >> 8 & 0xff }
            if len(self.pcmBuffer)  >= self.samplingRate * 4 / 5:
                aNow=time()
                self.alsaHandler.write(self.pcmBuffer)
                self.pcmBuffer = ""
        else:
            self.outputStream.write("%(c1)c%(c2)c" % {'c1' : leftChannel & 0xff, 'c2' : leftChannel >> 8 & 0xff})

            self.outputStream.write("%(c1)c%(c2)c" % {'c1' : rightChannel & 0xff, 'c2' : rightChannel >> 8 & 0xff})

class AlsaHandler:

    def __init__(self, pcm):
        self.pcm = pcm
        self.thread = None

    def write(self, data):
        if self.thread != None:
          while self.thread.isAlive():
            # Have to wait for it to finish
            None
        self.thread = AlsaThread(self.pcm, data)
        self.thread.start()

class AlsaThread(Thread):

    def __init__(self, pcm, data):
        Thread.__init__(self)
        self.pcm = pcm
        self.data = data

    def run(self):
        self.pcm.write(self.data)

if __name__ == "__main__":
    import math
    import sys
    argc = len(sys.argv)
    channel = None
    frequencies = list()
    if argc == 1:
        print("Have to provide frequencies to play during a second each"
        sys.exit(1)
    for i in range(1, argc):
        frequencies.append(float(sys.argv[i]))
    
    player = WavePlayer(11025)
    channel = Wave(frequencies[0], 11025)
    for i in frequencies:
        sys.stderr.write("Playing frequency " + str(i) + "\n")
        sys.stderr.flush()
        channel.setFrequency(i)
        for j in range(0, 11025):
            height = channel.getNextValue()
            player.play(height)

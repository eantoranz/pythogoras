#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2009 Edmundo Carmona Antoranz

# Released under the terms of the Affero GPLv3

import sys
from Wave import Wave
import os

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
                    sys.stderr.println("Trying to access alsa\n")
                import alsaaudio
                self.pcm = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NORMAL)
                self.pcm.setrate(samplingRate)
                self.pcm.setperiodsize(samplingRate)
                self.pcm.setchannels(2)
                self.pcm.setformat(alsaaudio.PCM_FORMAT_S16_BE)
                self.pcmBuffer = ""

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
            self.pcmBuffer += "%(c1)c%(c2)c%(c3)c%(c4)c" % {'c1' : leftChannel >> 8 & 0xff, 'c2' : leftChannel & 0xff, 'c3' : rightChannel >> 8 & 0xff, 'c4' : rightChannel & 0xff}
            if len(self.pcmBuffer)  >= self.samplingRate * 4:
                print "Ready to write data"
                self.pcm.write(self.pcmBuffer)
                print "Wrote data successfully"
                self.pcmBuffer = ""
        else:
            self.outputStream.write("%(c1)c%(c2)c" % {'c1' : leftChannel >> 8 & 0xff, 'c2' : leftChannel & 0xff})

            self.outputStream.write("%(c1)c%(c2)c" % {'c1' : rightChannel >> 8 & 0xff, 'c2' : rightChannel & 0xff})

if __name__ == "__main__":
    import math
    import sys
    argc = len(sys.argv)
    leftChannel = None
    rightChannel = None
    if argc == 1:
        print "Have to provide either a single frequency to play or a frequency for each channel (left first)"
        sys.exit(1)
    elif argc == 2:
        # Provided a single frequency for both channels
        leftChannel = Wave(float(sys.argv[1]))
    else:
        leftChannel = Wave(float(sys.argv[1]))
        rightChannel = Wave(float(sys.argv[2]))
    
    player = WavePlayer()
    while True:
        leftHeight = leftChannel.getNextValue()
        if rightChannel == None:
            rightHeight = leftHeight
        else:
            rightHeight = rightChannel.getNextValue()
        player.play(leftHeight, rightHeight)

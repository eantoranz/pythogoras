#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2009-2025 Edmundo Carmona Antoranz

# Released under the terms of the Affero GPLv3

import alsaaudio
import math
import os
import sys
from threading import Thread
from time import *

from Wave import Wave

class WavePlayer:

    def __init__(self, samplingRate=44100, outputStream=None, debug=False):
        self.samplingRate = samplingRate
        self.volume = 1
        self.debug = debug
        self.outputStream = outputStream
        self.pcm = None

        if outputStream == None:
            if debug:
                sys.stderr.write("Trying to open sound output\n")
            if os.name == "posix":
                if debug:
                    sys.stderr.write("Trying to access alsa\n")
                self.pcm = alsaaudio.PCM(
                    alsaaudio.PCM_PLAYBACK,
                    alsaaudio.PCM_NORMAL,
                    rate=samplingRate,
                    periodsize=int(samplingRate / 5),
                    channels=2,
                    format=alsaaudio.PCM_FORMAT_S16_LE,
                )
                self.pcmBuffer = bytearray()
                self.alsaHandler = AlsaHandler(self.pcm)
            else:
                print("Unknown OS: " + os.name)

    def setVolume(self, volume):
        if volume > 1:
            self.volume = 1
        elif volume < 0:
            self.volume = 0
        else:
            self.volume = volume

    def play(self, leftChannel, rightChannel=None):
        leftChannel *= int(self.volume)
        if rightChannel != None:
            rightChannel *= int(self.volume)
        else:
            rightChannel = leftChannel

        if self.debug:
            sys.stderr.write(
                "Left: " + str(leftChannel) + " Right: " + str(rightChannel) + "\n"
            )

        if leftChannel < 0:
            leftChannel = leftChannel ^ 0xFFFF + 1
        if rightChannel < 0:
            rightChannel = rightChannel ^ 0xFFFF + 1

        sample = bytearray()
        sample += (leftChannel & 0xFF).to_bytes()
        sample += ((leftChannel >> 8) & 0xFF).to_bytes()
        sample += (rightChannel & 0xFF).to_bytes()
        sample += ((rightChannel >> 8) & 0xFF).to_bytes()
        if self.outputStream == None:
            # PCM
            self.pcmBuffer += sample
            if len(self.pcmBuffer) >= self.samplingRate * 4 / 5:
                self.alsaHandler.write(self.pcmBuffer)
                self.pcmBuffer = bytearray()
        else:
            self.outputStream.write(sample)


class AlsaHandler:

    def __init__(self, pcm):
        self.pcm = pcm
        self.thread = None

    def write(self, data):
        if self.thread != None:
            while self.thread.is_alive():
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

SAMPLING_RATE = 48000

if __name__ == "__main__":

    argc = len(sys.argv)
    leftChannel = None
    rightChannel = None
    if argc == 1:
        print(
            "Have to provide either a single frequency to play or a frequency for each channel (left channel first)"
        )
        sys.exit(1)
    elif argc == 2:
        # Provided a single frequency for both channels
        leftChannel = Wave(float(sys.argv[1]), SAMPLING_RATE)
    else:
        leftChannel = Wave(float(sys.argv[1]), SAMPLING_RATE)
        rightChannel = Wave(float(sys.argv[2]), SAMPLING_RATE)

    player = WavePlayer(SAMPLING_RATE)
    while True:
        leftHeight = leftChannel.getNextValue()
        if rightChannel == None:
            rightHeight = leftHeight
        else:
            rightHeight = rightChannel.getNextValue()
        player.play(leftHeight, rightHeight)

# -*- coding: utf-8 -*-

# Copyright 2009 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

import math

class Wave:

    freq = None
    samplingRate = None
    maxValue = None
    binaryOuput = True
    counter = 0

    def __init__(self, freq, samplingRate = 44100, maxValue = 32000):
        self.freq = freq
        self.samplingRate = samplingRate
        self.maxValue = maxValue
        self.volume=1

        self.resetCounter()

    def resetCounter(self):
        self.counter = 0

    def getNextValue(self):
        if self.freq in [None, 0]:
            return 0

        temp = int(math.floor(math.sin(2 * math.pi * self.counter / self.samplingRate * self.freq) * self.maxValue) * self.volume)

        self.counter+=1
        return temp

    def getFrequency(self):
        return self.freq

    def setVolume(self, volume):
        if volume > 1:
            self.volume = 1
        elif volume < 0:
            self.volume = 0
        else:
            self.volume=volume

class ChangingWave(Wave):

    def __setFrequency(self, newFreq):
        """ Used to change the frequency of the wave to a new frequency """
        # let's calculate the point of the wave where it is right now
        ticksPerWave = self.samplingRate / self.freq
        mod = self.counter % ticksPerWave
        oldPosition = mod * 2 * math.pi / ticksPerWave
        # new ticks per wave TODO this can break the movement of the wave (ex: if we are going down between 0 and the bottom)
        self.freq = newFreq
        ticksPerWave = self.samplingRate / self.freq
        counter = int(oldPosition * ticksPerWave / (2 * math.pi))
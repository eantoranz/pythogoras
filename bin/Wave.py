# -*- coding: utf-8 -*-

# Copyright 2009 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

import math
import sys

class Wave:

    freq = None
    samplingRate = None
    maxValue = None
    binaryOuput = True
    counter = 0

    def __init__(self, freq, samplingRate = 44100, maxValue = 32000):
        if freq != None:
            self.freq = float(freq)
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
    
    def setFrequency(self, frequency):
        # will calculate new position based on the cycles that have gone by in the previous
        # frequency and the same cycles gone by on the new frequency
        samplesPerCycle = self.samplingRate / self.freq
        cyclePosition = self.position / samplesPerCycle
        self.freq = float(frequency)
        samplesPerCycle = salf.samplingRate / self.freq
        self.position = samplesPerCycle * cyclePosition
        
    # set the angle of the current position (in radians)
    # also, optionally, set a new frequency
    def setAngle(self, angle, frequency = None):
        if frequency == None:
            frequency = self.freq
        self.counter = angle * self.samplingRate / frequency / (2 * math.pi)
        self.freq = frequency
    
    def getAngle(self):
        if self.freq == None:
            #@TODO this shouldn't happen. Why does it happen?
            return 0
        sine = math.sin(2 * math.pi * self.counter / self.samplingRate * self.freq)
        cosine = math.cos(2 * math.pi * self.counter / self.samplingRate * self.freq)
        
        # let's find the "angle" of the wave at this moment in time
        angle = math.asin(sine) # in radians
        # if the cosine is negative, have to correct the position in the wave
        if cosine < 0:
            # have to correct the position of the angle to the other half
            # check this because this could be why there is a gap when changing frequencies close to the peaks
            angle = math.pi - angle
        
        return angle

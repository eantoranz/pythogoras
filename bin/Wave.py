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


class SynthWave(Wave):
    """
        This wave can read from a sampling file and reproduce the wave as in the sampling file with the desired frequency
        
        The sampling file has to contain (at least for the moment) a single wave cycle. It can be any length and the sampling
        size will be used to calculate the original wave frquency
        
        Format of the sampling file:
        RAW PCM signed 16 bit mono, 44.1 khtz, little endian
    """
    
    samples = []

    def __init__(self, samplingFile, freq, samplingRate = 44100, maxValue = 32000):
        Wave.__init__(self, freq, samplingRate, maxValue)
        
        # let's read the sampling file
        inputFile = open(samplingFile, 'r')
        # now we start reading numbers
        while (True):
            value = inputFile.read(2)
            if (len(value) < 2):
                # sample was incomplete.... we go out
                break
            # now we create the numeric sample
            sample = 0;
            for i in xrange(2):
                sample = sample << 8 | ord(value[i])
            if (sample & 0x80 != 0):
                sample = ~sample + 1
            self.samples.append(sample)
            print sample

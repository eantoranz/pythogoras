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
    
    def setFrequency(self, frequency):
        #sys.stderr.write("Switching frequency from " + 
        # now that the frequency is going to change, we have to recalculate the new counter value that corresponds to the actual
        # height of the wave at this point but for the new frequency
        sine = math.sin(2 * math.pi * self.counter / self.samplingRate * self.freq)
        sys.stderr.write("Sine: " + str(sine) + "\n")
        cosine = math.cos(2 * math.pi * self.counter / self.samplingRate * self.freq)
        sys.stderr.write("Cosine: " + str(cosine) + "\n")
        # let's find the arc sine of this wave at this height
        newpos = math.asin(sine) # in radians
        sys.stderr.write("New pos: " + str(newpos) + " radians\n")
        # if the cosine is negative, have to correct the position in the wave
        if cosine < 0:
            # have to correct the position of the counter to the other half
            newpos = math.pi - newpos
            sys.stderr.write("Cosine is negative. New pos is " + str(newpos) + " radians\n")
        #self.counter = int(math.floor(newpos * self.samplingRate * self.freq) / (2 * math.pi))
        self.counter = int(math.floor(newpos * self.samplingRate / (2 * math.pi)))
        sys.stderr.write("New counter position is " + str(self.counter) + " / " + str(self.samplingRate) + ")\n")
        self.freq = frequency
        

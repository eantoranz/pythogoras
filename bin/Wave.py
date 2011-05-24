# -*- coding: utf-8 -*-

# Copyright 2009 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

import math
import sys
from threading import Thread

class Wave(Thread):

    freq = None
    samplingRate = None
    maxValue = None
    binaryOuput = True
    counter = 0
    
    nextVal = None

    def __init__(self, freq, samplingRate = 44100, maxValue = 32000):
        Thread.__init__(self)
        self.freq = freq
        self.samplingRate = samplingRate
        self.maxValue = maxValue
        self.volume=1

        self.resetCounter()
        
        self.start()

    def resetCounter(self):
        self.counter = 0

    def getNextValue(self):
        while self.nextVal == None:
            # tight loop.. perhaps too tight
            # could be solved with blocking?
            continue
        temp = self.nextVal
        self.nextVal = None
        # calculate another next value
        self.start()
        return temp
    
    def run(self):
        self.calculateNextVal()

    def calculateNextVal(self):
        if self.freq in [None, 0]:
            self.nextVal = 0
            return

        self.nextVal = int(math.floor(math.sin(2 * math.pi * self.counter / self.samplingRate * self.freq) * self.maxValue) * self.volume)

        self.counter+=1

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
        angle = self.getAngle()
        self.setAngle(angle, frequency)
        
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

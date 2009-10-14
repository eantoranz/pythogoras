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
        self.frep = freq
        self.samplingRate = samplingRate
        self.maxValue = maxValue

        self.resetCounter()

    def resetCounter(self):
        self.counter = 0

    def getNextValue(self):
        temp = math.floor(math.sin(2 * math.pi * self.counter / self.samplingRate) * self.maxValue)

        self.counter+=1
        return temp

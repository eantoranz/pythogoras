# -*- coding: utf-8 -*-

# Copyright 2013 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

from Wave import Wave

class Sampler:
    
    def __init__(self, totalHarmonics = 8):
        """
            We will only use a defined number of harmonics to synthesyze sound
        """
    
    def getWave(self, frequency, samplingRate = 44100, maxValue = 32000):
        """
            This method has to be overwriten by the sampler and has to return a Wave instance
        """
        return Wave(frequency, samplingRate, maxValue)
        
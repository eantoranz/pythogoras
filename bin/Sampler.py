# -*- coding: utf-8 -*-

# Copyright 2009 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

from Wave import *
from numpy import fft
import sys
import math

class Sampler:
    """
        This wave can read from a sampling file and reproduce the wave as in the sampling file with the desired frequency
        
        The sampling file has to contain (at least for the moment) a single wave cycle. It can be any length and the sampling
        size will be used to calculate the original wave frequency
        
        Format of the sampling file:
        RAW PCM signed 16 bit mono, 44.1 khtz, little endian
    """
    
    def __init__(self, samplingFile, harmonics = 5):
        """
            We will only use a defined number of harmonics to synthesyze sound
        """
        self.sampleFreq = None # Frequency of the sample
        self.samples = []
        self.origLevels = []
    
        # peak stuff
        self.peaks = dict()
        self.orderedPeaks = dict()
        self.highestPeakLevel = None

        # let's read the sampling file
        inputFile = open(samplingFile, 'r')
        # now we start reading numbers
        while (True):
            value = inputFile.read(2)
            if (len(value) < 2):
                # sample was incomplete.... we go out
                break
            # now we create the numeric sample
            sample = ord(value[1]) << 8 | ord(value[0]);
            if (sample & 0x8000 != 0):
                sample -= 0x10000
            self.samples.append(sample)
        
        # let's see what numpy has for us
        fftRes = fft.fft(self.samples)
        freqStep = 44100.0 / len(fftRes)
        freq = 0
        level = None # current level
        peakLevel = None # peak level in a segment
        peakFreq = None # peak freq in a segment
        minLevel = None

        for element in fftRes:
            if freq * 2 > 44100.0:
                # that's it
                break
            level = pow(pow(element.real, 2) + pow(element.imag, 2), 0.5)
            if (freq > 0):
                self.origLevels.append(level)
            if minLevel == None:
                minLevel = level # this is the average level, right? Will only consider a single peak per each segment that crosses this value
            else:
                # this is a level... is it over or under minLevel?
                if (level < minLevel):
                    # Ok.... we are under minLevel... did we have a peak?
                    if peakLevel != None:
                        # yes, ye had a peak
                        self.orderedPeaks[peakLevel] = peakFreq
                        if self.highestPeakLevel == None or self.highestPeakLevel < peakLevel:
                            self.highestPeakLevel = peakLevel
                        peakFreq = None
                        peakLevel = None
                    else:
                        # no previous peak so nothing to do
                        None
                else:
                    # we are at least at the min level
                    if peakLevel == None or peakLevel < level:
                        peakFreq = freq
                        peakLevel = level
            freq += freqStep
        
        # let's save the highest peaks
        # and the lowest (probably base) frequency
        self.baseFreq = None
        for level in sorted(self.orderedPeaks.iterkeys(), reverse=True)[0:harmonics]:
            freq = self.orderedPeaks[level]
            if self.baseFreq == None or self.baseFreq > freq:
                self.baseFreq = freq
            self.peaks[freq] = level / self.highestPeakLevel

    def getY(self, index):
        """
            Index is a value between 0 and 1 (0 = cycle start, 1 = cycle end)
            Will return a value between 1 and -1
        """
        # first, we have to find the "real" index that we have to use for that 0-1 index
        # 0 = self.x0index
        # 1 = self.x1index
        realIndex = self.x0index + (self.x1index - self.x0index) * index
        # now we can calculate the values involved
        beforeIndex = math.floor(realIndex)
        beforeValue = self.samples[int(beforeIndex)]
        if (beforeIndex == realIndex):
            # a perfect match... let's use that value directly
            return float(beforeValue) / 0x8000
        # it's a value in between
        # let's do a lineal function aprox
        afterValue = self.samples[int(beforeIndex + 1)]
        
        # now we do the lineal calculation
        if (beforeIndex == 0):
            return afterValue * float(realIndex - self.x0index) / 0x8000
        return (beforeValue + (afterValue - beforeValue) * float(realIndex - beforeIndex)) / 0x8000

class SamplerWave(Wave):
  
    sampler = None
    samplesPerCycle = None
    
    def __init__(self, sampler, freq, samplingRate = 44100, maxValue = 32000):
        Wave.__init__(self, freq, samplingRate, maxValue)
        self.sampler = sampler
        if self.freq not in [0, None]:
            self.samplesPerCycle = float(self.samplingRate) / self.freq
    
    def getNextValue(self):
        if self.freq in [None, 0]:
            return 0

        # we need to know the current position in the wave
        res = self.sampler.getY(float(self.counter) / self.samplesPerCycle)
        
        # increase the step counter
        self.counter += 1
        if (self.counter >= self.samplesPerCycle):
            self.counter -= self.samplesPerCycle
        
        return int(self.volume * self.maxValue * res)

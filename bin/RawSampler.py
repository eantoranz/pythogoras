# -*- coding: utf-8 -*-

# Copyright 2013 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

from Sampler import *
from Wave import *
from numpy import fft
import sys
import math

class RawSampler(Sampler):
    """
        This wave can read from a sampling file and reproduce the wave as in the sampling file with the desired frequency
        
        The sampling file has to contain (at least for the moment) a single wave cycle. It can be any length and the sampling
        size will be used to calculate the original wave frequency
        
        Format of the sampling file:
        RAW PCM signed 16 bit mono, 44.1 khtz, little endian
    """
  
    def __init__(self, samplingFile, totalHarmonics = 8, peaksForAnalysis = 3):
        """
            We will also consider so many peaks to find base freq
        """
        Sampler.__init__(self, totalHarmonics)
        self.baseFreq = None
        self.samples = []
        self.origLevels = []
    
        # peak stuff
        self.harmonics = list() # level to use for the different harmonics (self.harmonics[0] is level for base frequency)
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
        level = None # current level
        peakLevel = None # peak level in a segment
        peakIndex = None # peak freq index in a segment
        minLevel = None

        freqIndex = 0
        freq = 0
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
                        # yes, we had a peak
                        self.orderedPeaks[peakLevel] = peakIndex
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
                        peakIndex = freqIndex
                        peakLevel = level
            freqIndex += 1
            freq += freqStep
        
        # let's save the highest peaks
        # and the lowest (probably base) frequency
        baseFreqIndex = None
        for level in sorted(self.orderedPeaks.iterkeys(), reverse=True)[0:peaksForAnalysis]:
            freqIndex = self.orderedPeaks[level]
            if baseFreqIndex == None or baseFreqIndex > freqIndex:
                baseFreqIndex = freqIndex
        self.baseFreq = freqStep * baseFreqIndex
        
        # Now let's check the levels of each harmonic
        harmonicCount = 0
        highestHarmonicLevel = None
        while harmonicCount < totalHarmonics or harmonicCount * baseFreqIndex >= len(self.origLevels):
            harmonicCount += 1
            harmonicIndex = harmonicCount * baseFreqIndex
            # level = self.origLevels[harmonicIndex - 1]
            level = self.getPeak(harmonicIndex - 1, harmonicCount * 2)
            if highestHarmonicLevel == None or highestHarmonicLevel < level:
                highestHarmonicLevel = level
            self.harmonics.append(level)

        # now we normalize the levels
        i = 0
        while i < len(self.harmonics):
            self.harmonics[i] = self.harmonics[i] / highestHarmonicLevel
            i += 1
    
    def getPeak(self, freqIndex, dispersion = 1):
        """
           Will look between the freqIndex+-dispersion levels and return the hightest value
        """
        i = freqIndex - dispersion
        if i < 0:
            i = 0
        peakLevel = None
        while i <= freqIndex + dispersion:
            level = self.origLevels[i]
            if peakLevel is None or peakLevel < level:
                peakLevel = level
            i += 1
        return peakLevel
    
    def getWave(self, frequency, samplingRate = 44100, maxValue = 32000):
        return RawSamplerWave(self, frequency, samplingRate, maxValue)
        
class RawSamplerWave(Wave):
  
    def __init__(self, sampler, freq, samplingRate = 44100, maxValue = 32000):
        Wave.__init__(self, freq, samplingRate, maxValue)
        if freq in [0, None]:
            return
        self.sampler = sampler
        self.waves = []
        # Now I have to create as many waves as harmonics in the sample
        factor = freq / sampler.baseFreq
        harmonicIndex = 0
        for level in sampler.harmonics:
            harmonicIndex += 1
            freq = sampler.baseFreq * harmonicIndex
            wave = Wave(freq * factor, samplingRate, maxValue)
            wave.setVolume(level)
            self.waves.append(wave)
        
    def getNextValue(self):
        if self.freq in [None, 0]:
            return 0

        # we trust on each wave
        sumValue = 0
        for wave in self.waves:
            sumValue += wave.getNextValue()
        
        return int(sumValue / len(self.waves) * self.volume)

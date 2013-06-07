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
    
    def __init__(self, samplingFile, harmonics = 8):
        """
            We will only use a defined number of harmonics to synthesyze sound
        """
        self.baseFreq = None
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
        for level in sorted(self.orderedPeaks.iterkeys(), reverse=True)[0:harmonics]:
            freq = self.orderedPeaks[level]
            if self.baseFreq == None or self.baseFreq > freq:
                self.baseFreq = freq
            self.peaks[freq] = level / self.highestPeakLevel

class SamplerWave(Wave):
  
    def __init__(self, sampler, freq, samplingRate = 44100, maxValue = 32000):
        Wave.__init__(self, freq, samplingRate, maxValue)
        if freq in [0, None]:
            return
        self.sampler = sampler
        self.waves = []
        # Now I have to create as many waves as harmonics in the sample
        sys.stderr.write("Requested Freq: " + str(freq) + "\n")
        sys.stderr.write("Sample base Freq: " + str(sampler.baseFreq) + "\n")
        factor = freq / sampler.baseFreq
        for freq in sampler.peaks.iterkeys():
            level = sampler.peaks[freq]
            sys.stderr.write("Creating a wave with freq " + str(freq * factor) + " and volume " + str(level) + "\n")
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
        #sys.stderr.write("Sum: " + str(sumValue) + " " + str(self.volume) + "\n")
        
        return int(sumValue / len(self.waves) * self.volume)

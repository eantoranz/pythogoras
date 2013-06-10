# -*- coding: utf-8 -*-

# Copyright 2013 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

import os
import sys
from Wave import Wave

class SharcSampler:
    """
        SharcSampler will use SHARC defitions (older format) for instrument timbre representation
        root directory of sharc should be in /usr/share/sharc
    """
    
    def __init__(self, instrumentName, totalHarmonics = 8):
        """
            We will only use a defined number of harmonics to synthesyze sound
        """
        self.harmonics = []
        
        # let's try to find instrument
        dirName = "/usr/share/sharc/" + instrumentName
        if not os.path.exists(dirName):
            raise Exception("SHARC Instrument definition directory does not exist\n")
        if not os.path.isdir(dirName):
            raise Exception("SHARC Instrument definition directory is not an actual directory\n")
        # We check into CONTENTS
        contents = open(dirName + "/CONTENTS", 'r')
        
        # first line will hold the lowest note which we will use as the timbre defition (at least for the time being)
        firstLine = contents.readline().strip().split(" ")
        contents.close()
        # What's the lowest sound defition?
        firstSound = firstLine[0].strip()
        # we got for that file
        firstSoundFile = open(dirName + "/" + firstSound + ".spect", 'r')
        # we read so many harmonics
        i = 0
        while (i < totalHarmonics):
            line = firstSoundFile.readline()
            if line == None:
                # reached EOF, don't have so many harmonics
                break
            # so we have a line.... what's the value for this harmonic?
            level = line.strip().split(" ")[0] # in dB
            self.harmonics.append(1 * pow(10, float(level) / 10))
            i += 1
        firstSoundFile.close()
    
    def getWave(self, frequency, samplingRate = 44100, maxValue = 32000):
        """
            This method has to be overwriten by the sampler and has to return a Wave instance
        """
        return SharcSamplerWave(self, frequency, samplingRate, maxValue)

class SharcSamplerWave(Wave):

    def __init__(self, sampler, freq, samplingRate, maxValue):
        Wave.__init__(self, freq, samplingRate, maxValue)
        if freq in [0, None]:
            return
        self.sampler = sampler
        self.waves = []
        # Now I have to create as many waves as harmonics in the sample
        harmonicIndex = 0
        baseFreq = freq
        for level in sampler.harmonics:
            harmonicIndex += 1
            freq = baseFreq * harmonicIndex
            wave = Wave(freq, samplingRate, maxValue)
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
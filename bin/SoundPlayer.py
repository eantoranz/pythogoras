#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2009 Edmundo Carmona Antoranz

# Released under the terms of the Affero GPLv3

import sys
from Wave import Wave

class SoundPlayer:

    def __init__(self, samplingRate = 44100, debug = False):
        self.samplingRate = samplingRate
        self.volume=1
        self.debug = debug

    def setVolume(self, volume):
        if volume > 1:
            self.volume=1
        elif volume < 0:
            self.volume = 0
        else:
            self.volume=volume

    def play(self, leftChannel, rightChannel):
        leftChannel *= int(self.volume)
        rightChannel *= int(self.volume)

        if self.debug:
            sys.stderr.write("Left: " + str(leftChannel) + " Right: " + str(rightChannel) + "\n")

        if leftChannel < 0:
            leftChannel = leftChannel ^ 0xffff + 1
        if rightChannel < 0:
            rightChannel = rightChannel ^ 0xffff + 1

        sys.stdout.write("%(c1)c%(c2)c" % {'c1' : leftChannel >> 8 & 0xff, 'c2' : leftChannel & 0xff})

        sys.stdout.write("%(c1)c%(c2)c" % {'c1' : rightChannel >> 8 & 0xff, 'c2' : rightChannel & 0xff})

if __name__ == "__main__":
    import math
    counter = 0
    wave = Wave(440)
    player = SoundPlayer()
    while counter < 44100:
        height = wave.getNextValue()
        player.play(height, height)

        counter += 1

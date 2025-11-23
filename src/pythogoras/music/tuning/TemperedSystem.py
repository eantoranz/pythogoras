# -*- coding: utf-8 -*-

# Copyright 2009-2025 Edmundo Carmona Antoranz
# For licensing terms, check docs/LICENSING.txt

import math

from pythogoras.music.tuning.TuningSystem import TuningSystem


class TemperedSystem(TuningSystem):

    instance = None

    def __init__(self, baseFreq=None):
        if baseFreq == None:
            self.baseFreq = TuningSystem.FREQ_A4
        else:
            self.baseFreq = baseFreq

    @classmethod
    def getInstance(cls):
        if TemperedSystem.instance == None:
            TemperedSystem.instance = TemperedSystem()
        return TemperedSystem.instance

    def getFrequency(self, note):
        if note.note in [None, 0]:
            return None
        distance = TuningSystem.A4.getDistance(note)
        return math.pow(2, float(distance[0] + distance[1]) / 12) * self.baseFreq

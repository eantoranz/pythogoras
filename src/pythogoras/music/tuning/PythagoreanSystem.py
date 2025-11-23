# -*- coding: utf-8 -*-

# Copyright 2009-2025 Edmundo Carmona Antoranz
# For licensing terms, check docs/LICENSING.txt

import math

from .TuningSystem import TuningSystem


class PythagoreanSystem(TuningSystem):

    instance = None  # default instance with 440 htz for A4

    DIATONIC_NUMERATOR = 256
    DIATONIC_DENOMINATOR = 243

    CHROMATIC_NUMERATOR = 243 * 9
    CHROMATIC_DENOMINATOR = 256 * 8

    def __init__(self, A4Freq=440):
        self.A4Freq = A4Freq

    @classmethod
    def getInstance(cls):
        if PythagoreanSystem.instance == None:
            PythagoreanSystem.instance = PythagoreanSystem()
        return PythagoreanSystem.instance

    def getFrequency(self, note):
        if note.note in [None, 0]:
            return None
        distance = TuningSystem.A4.getDistance(note)
        return (
            self.A4Freq
            * math.pow(PythagoreanSystem.DIATONIC_NUMERATOR, distance[0])
            / math.pow(PythagoreanSystem.DIATONIC_DENOMINATOR, distance[0])
            * math.pow(PythagoreanSystem.CHROMATIC_NUMERATOR, distance[1])
            / math.pow(PythagoreanSystem.CHROMATIC_DENOMINATOR, distance[1])
        )

# -*- coding: utf-8 -*-

# Copyright 2009-2025 Edmundo Carmona Antoranz
# For licensing terms, check docs/LICENSING.txt

from pythogoras.music.MusicalNote import MusicalNote
from .PythagoreanSystem import PythagoreanSystem
from .TuningSystem import TuningSystem


class JustSystem(TuningSystem):

    rates = [
        [1, 1],  # JUST FIRST
        [16, 15],  # AUGMENTED FIRST
        [9, 8],  # MAJOR_SECOND
        [6, 5],  # AUGMENTED SECOND
        [5, 4],  # MAJOR THIRD
        [4, 3],  # JUST_FOURTH
        [32, 23],  # AUGMENTED_FOURTH
        [3, 2],  # JUST_FIFTH
        [8, 5],  # AUGMENTED_FIFTH
        [5, 3],  # MAJOR_SIXTH
        [16, 9],  # MINOR_SEVENTH
        [15, 8],
    ]  # MAJOR_SEVENTH

    def __init__(self, note, alteration, baseFreq=None):
        # right now, can only use major scales to tune
        self.note = note
        self.alteration = alteration
        self.baseNote = MusicalNote(note, alteration, 4)
        pytha = PythagoreanSystem.getInstance()
        # find the frequency of the base sound between C4 and B4
        if baseFreq == None:
            self.baseFreq = pytha.getFrequency(self.baseNote)
        else:
            self.baseFreq = baseFreq

    def getFrequency(self, note):
        if note.note in [None, 0]:
            return None
        # calculate the distance between the base sound and the note that was provided
        distance = self.baseNote.getDistance(note)
        # let's sum up both types of semitones to start working
        distance = distance[0] + distance[1]
        if distance == 0:
            # nothing else to do
            return self.baseFreq
        freq = self.baseFreq
        if distance > 0:
            while distance >= 12:
                freq *= 2
                distance -= 12
        else:
            while distance < 0:
                freq /= 2
                distance += 12
        rate = JustSystem.rates[distance]
        return freq * rate[0] / rate[1]

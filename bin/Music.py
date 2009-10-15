# -*- coding: utf-8 -*-

# Copyright 2009 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

import math

class MusicalNote:

    # static members
    NOTE_A = 1
    NOTE_B = 2
    NOTE_C = 3
    NOTE_D = 4
    NOTE_E = 5
    NOTE_F = 6
    NOTE_G = 7

    #instance members
    note = None
    alter = None
    index = None

    def __init__(self, note, alter, index):
        self.note = note
        self.alter = alter
        self.index = index

    # Will return a tuple. index 0 is diatonic and index 1 is chromatic
    def getDistance(self, note2):
        if self.index > note2.index:
            temp = note2.getDistance(self)
            return [-temp[0], -temp[1]]
        if self.index == note2.index:
            # indexes are the same... have to compare the notes
            if self.note > note2.note:
                temp = note2.getDistance(self)
                return [-temp[0], -temp[1]]
            if self.note == note2.note:
                # the difference is chromatic
                return [0, note2.alter - self.alter]

        # self is a lower note, for sure
        diatonic = 7 * (note2.index - self.index)
        chromatic = 5 * (note2.index - self.index)

        if self.note == MusicalNote.NOTE_D:
            diatonic -= 1
            chromatic -= 1
        elif self.note == MusicalNote.NOTE_E:
            diatonic -= 2
            chromatic -= 2
        elif self.note == MusicalNote.NOTE_F:
            diatonic -= 3
            chromatic -= 2
        elif self.note == MusicalNote.NOTE_G:
            diatonic -= 4
            chromatic -= 3
        elif self.note == MusicalNote.NOTE_A:
            diatonic -= 5
            chromatic -= 4
        elif self.note == MusicalNote.NOTE_B:
            diatonic -= 6
            chromatic -= 5

        if note2.note == MusicalNote.NOTE_D:
            diatonic += 1
            chromatic += 1
        elif note2.note == MusicalNote.NOTE_E:
            diatonic += 2
            chromatic += 2
        elif note2.note == MusicalNote.NOTE_F:
            diatonic += 3
            chromatic += 2
        elif note2.note == MusicalNote.NOTE_G:
            diatonic += 4
            chromatic += 3
        elif note2.note == MusicalNote.NOTE_A:
            diatonic += 5
            chromatic += 4
        elif note2.note == MusicalNote.NOTE_B:
            diatonic += 6
            chromatic += 5

        chromatic += note2.alter - self.alter

        return [diatonic, chromatic]

    def toString(self):
        temp = None
        if self.note == MusicalNote.NOTE_A:
            temp = "A"
        elif self.note == MusicalNote.NOTE_B:
            temp = "B"
        elif self.note == MusicalNote.NOTE_C:
            temp = "C"
        elif self.note == MusicalNote.NOTE_D:
            temp = "D"
        elif self.note == MusicalNote.NOTE_E:
            temp = "E"
        elif self.note == MusicalNote.NOTE_F:
            temp = "F"
        elif self.note == MusicalNote.NOTE_G:
            temp = "G"
        if self.alter != 0:
            if self.alter > 0:
                temp += (self.alter * "#")
            else:
                temp += (-self.alter * 'b')
        temp += str(self.index)
        return temp
        
class TuningSystem:

    FREQ_A4 = 440
    A4 = MusicalNote(MusicalNote.NOTE_A, 0, 4)

    def getFrequency(self, note):
        return 0


class TemperedSystem(TuningSystem):

    instance = None

    @classmethod
    def getInstance(cls):
        if (TemperedSystem.instance == None):
            TemperedSystem.instance = TemperedSystem()
        return TemperedSystem.instance

    def getFrequency(self, note):
        distance = TuningSystem.A4.getDistance(note)
        return math.pow(2, float(distance[0] + distance[1]) / 12) * TuningSystem.FREQ_A4

class PythagoreanSystem(TuningSystem):

    instance = None

    DIATONIC_NUMERATOR = 256
    DIATONIC_DENOMINATOR = 243

    CHROMATIC_NUMERATOR = 243 * 9
    CHROMATIC_DENOMINATOR = 256 * 8

    @classmethod
    def getInstance(cls):
        if (PythagoreanSystem.instance == None):
            PythagoreanSystem.instance = PythagoreanSystem()
        return PythagoreanSystem.instance

    def getFrequency(self, note):
        distance = TuningSystem.A4.getDistance(note)
        return TuningSystem.FREQ_A4 * math.pow(PythagoreanSystem.DIATONIC_NUMERATOR, distance[0]) / math.pow(PythagoreanSystem.DIATONIC_DENOMINATOR, distance[0]) \
            * math.pow(PythagoreanSystem.CHROMATIC_NUMERATOR, distance[1]) / math.pow(PythagoreanSystem.CHROMATIC_DENOMINATOR, distance[1])
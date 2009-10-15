# -*- coding: utf-8 -*-

# Copyright 2009 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

from math import *

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
    def getDifference(self, note2):
        if self.index > note2.index:
            temp = note2.getDifference(self)
            return [-temp[0], -temp[1]]
        if self.index == note2.index:
            # indexes are the same... have to compare the notes
            if self.note > note2.note:
                temp = note2.getDifference(self)
                return [-temp[0], -temp[1]]
            if self.note == note2.note:
                # the difference is chromatic
                return [0, note2.alter - self.alter]

        # self is a lower note, for sure
        diatonic = 5 * (note2.index - self.index)
        chromatic = 7 * (note2.index - self.index)

        diatonic += (note2.note - self.note)
        # let's count the difference of half notes between notes
        if self.note > MusicalNote.NOTE_B:
            diatonic -= 1
        if self.note > MusicalNote.NOTE_E:
            diatonic -= 1
        if note2.note > MusicalNote.NOTE_B:
            diatonic += 1
        if note2.note > MusicalNote.NOTE_E:
            diatonic += 1

        chromatic += note2.alter - self.alter

        return [diatonic, chromatic]
        
class Music:

    FREQ_A4 = 440

    @classmethod
    def getDifferenceBetweenNotes(cls, note1, note2):
        if (note1.index > note2.index):
            return self.getDifferenceBetweenNotes()
        chromatic = note1.alter - note2.alter
        diatonic = 0
        
        

    

class TuningSystem:

    def __init__(self):
        print("Hi!")


    
# -*- coding: utf-8 -*-

# Copyright 2009 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

import math
import sys

class MusicalNote:

    # static members
    NOTE_A = 1
    NOTE_B = 2
    NOTE_C = 3
    NOTE_D = 4
    NOTE_E = 5
    NOTE_F = 6
    NOTE_G = 7

    def __init__(self, note, alter, index, duration = None, dotted = False):
        """
            Create a new note. if note = None or zero, it's a rest
        """
        self.note = note
        self.alter = alter
        self.index = index
        self.duration = None
        self.dotted = dotted # could be a number later on but right now it's just True/False
        if duration != None:
            self.setDuration(duration)

    def setDuration(self, duration):
        # Can be a number (1, 2, 4, 8, 16, 32, 64) or a number followed by a dot
        pos = str(duration).find('.')
        if pos != -1:
            # dotted
            self.duration = int(duration[0:pos - 1])
            self.dotted = True
        else:
           self.duration = int(duration)
        

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

    def toString(self, showDuration = True):
        temp = None
        if self.note in [None, 0]:
            temp = "r"
        elif self.note == MusicalNote.NOTE_A:
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
        if self.note not in [None, 0]:
            temp += str(self.index)
        if showDuration:
            temp += "<" + str(self.duration)
            if (self.dotted):
                temp += "."
            temp += ">"
        return temp

    def __str__(self):
        return self.toString()

class MusicalChord:

    def __init__(self, notes, duration):
        self.notes = notes
        for note in notes:
            note.setDuration(duration)
    
    def toString(self):
        temp = "Chord. Duration: " + str(self.notes[0].duration)
        if self.notes[0].dotted:
            temp += '.'
        temp += " Notes: "

        firstNote = True
        for note in self.notes:
            if firstNote:
                firstNote = False
            else:
                temp += " "
            temp += note.toString(False)
        return temp

    def __str__(self):
        return self.toString()

    def getDuration(self):
        return self.notes[0].duration

    def isDotted(self):
        return self.notes[0].dotted

class MusicalPolyphony:

    def __init__(self, voices):
        self.voices = voices
    
    def toString(self):
        temp = "Polyphonic voice\n"
        counter = 1
        for voice in self.voices:
            temp += "Voice " + str(counter) + ":"
            for element in voice:
                temp += " " + str(element)
            temp += "\n"
            counter+=1
        
class MusicalKey:

    def __init__(self, note, alteration, major):
        self.note = note
        self.alteration = alteration
        self.major = major

    def toString(self):
        if self.note == MusicalNote.NOTE_A:
            note = 'A'
        elif self.note == MusicalNote.NOTE_B:
            note = 'B'
        elif self.note == MusicalNote.NOTE_C:
            note = 'C'
        elif self.note == MusicalNote.NOTE_D:
            note = 'D'
        elif self.note == MusicalNote.NOTE_E:
            note = 'E'
        elif self.note == MusicalNote.NOTE_F:
            note = 'F'
        elif self.note == MusicalNote.NOTE_G:
            note = 'G'
        else:
            raise Exception('Unknown note in musical key: ' + str(self.note))

        if self.alteration < 0:
            alteration = (self.alteration * -1) * 'b'
        elif self.alteration > 0:
            alteration = self.alteration * '#'
        else:
            alteration = ''

        if self.major:
            major = 'Major'
        else:
            major = 'Minor'
            
        return "Key: " + note + alteration + " " + major

    def __str__(self):
        return self.toString()

class TuningSystem:

    FREQ_A4 = 440
    A4 = MusicalNote(MusicalNote.NOTE_A, 0, 4)

    def getFrequency(self, note):
        return 0


class TemperedSystem(TuningSystem):

    instance = None

    def __init__(self, baseFreq = None):
        if baseFreq == None:
            self.baseFreq = TuningSystem.FREQ_A4
        else:
            self.baseFreq = baseFreq

    @classmethod
    def getInstance(cls):
        if (TemperedSystem.instance == None):
            TemperedSystem.instance = TemperedSystem()
        return TemperedSystem.instance

    def getFrequency(self, note):
        if note.note in [None, 0]:
            return None
        distance = TuningSystem.A4.getDistance(note)
        return math.pow(2, float(distance[0] + distance[1]) / 12) * self.baseFreq

class PythagoreanSystem(TuningSystem):

    instance = None # default instance with 440 htz for A4

    DIATONIC_NUMERATOR = 256
    DIATONIC_DENOMINATOR = 243

    CHROMATIC_NUMERATOR = 243 * 9
    CHROMATIC_DENOMINATOR = 256 * 8

    def __init__(self, A4Freq = 440):
        self.A4Freq = A4Freq

    @classmethod
    def getInstance(cls):
        if (PythagoreanSystem.instance == None):
            PythagoreanSystem.instance = PythagoreanSystem()
        return PythagoreanSystem.instance

    def getFrequency(self, note):
        if note.note in [None, 0]:
            return None
        distance = TuningSystem.A4.getDistance(note)
        return self.A4Freq * math.pow(PythagoreanSystem.DIATONIC_NUMERATOR, distance[0]) / math.pow(PythagoreanSystem.DIATONIC_DENOMINATOR, distance[0]) \
            * math.pow(PythagoreanSystem.CHROMATIC_NUMERATOR, distance[1]) / math.pow(PythagoreanSystem.CHROMATIC_DENOMINATOR, distance[1])

class JustSystem(TuningSystem):

    rates = [[1, 1], # JUST FIRST
        [16, 15], # AUGMENTED FIRST
        [9, 8], # MAJOR_SECOND
        [6, 5], # AUGMENTED SECOND
        [5, 4], # MAJOR THIRD
        [4, 3], # JUST_FOURTH
        [32, 23], # AUGMENTED_FOURTH
        [3, 2], # JUST_FIFTH
        [8, 5], # AUGMENTED_FIFTH
        [5, 3], # MAJOR_SIXTH
        [16, 9], # MINOR_SEVENTH
        [15, 8]] # MAJOR_SEVENTH

    def __init__(self, note, alteration, baseFreq = None):
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
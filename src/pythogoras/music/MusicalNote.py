# -*- coding: utf-8 -*-

# Copyright (c) 2009-2025 Edmundo Carmona Antoranz
# For licensing terms, check docs/LICENSING.txt


class MusicalNote:

    # static members
    NOTE_A = 1
    NOTE_B = 2
    NOTE_C = 3
    NOTE_D = 4
    NOTE_E = 5
    NOTE_F = 6
    NOTE_G = 7

    def __init__(self, note, alter, index, duration=None, dots=None, times=None):
        """
        Create a new note. if note = None or zero, it's a rest
        """
        self.note = note
        self.alter = alter
        self.index = index
        self.duration = None
        self.dots = dots  # 0 means no dot. 1 single dot, and so on @TODO it's being overwritten on setDuration
        self.times = times
        if duration != None:
            self.setDuration(duration)

    def setDuration(self, duration, analyzeDots=False):
        duration = str(duration)
        # Can be a number (1, 2, 4, 8, 16, 32, 64) or a number followed by some dots

        # if the duration has dots, skip pver them
        firstDotPos = str(duration).find(".")
        if firstDotPos == -1:
            # there is only the duration of the note
            self.duration = int(duration)
        else:
            self.duration = int(duration[0:firstDotPos])
            if analyzeDots:
                dots = 0
                pos = firstDotPos
                while pos < len(duration) and duration[pos] == ".":
                    dots += 1
                    pos += 1
                # finished dots
                self.dots = dots

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

    def toString(self, showDuration=True):
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
                temp += self.alter * "#"
            else:
                temp += -self.alter * "b"
        if self.note not in [None, 0]:
            temp += str(self.index)
        if showDuration and self.duration:
            temp += "<" + str(self.duration)
            if self.dots is not None and self.dots > 0:
                for i in range(self.dots):
                    temp += "."
            temp += ">"
        return temp

    def __str__(self):
        return self.toString()

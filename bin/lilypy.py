#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2009 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

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

    def __repr__(self):
        return self.toString()


class LilypondHeader:

    def __init__(self):
        """
            Nothing yet
        """

class LilypondAnalyser:

    def __init__(self):
        self.header = None
        self.tokens = []

    def readTokens(self, lines):
        for line in lines:
            token = "" # Starting a line, word is empty
            for char in line:
                if char == " " or char == "\t":
                    # space or tab
                    if len(token) > 0:
                        # there is something in the token
                        self.tokens.append(token)
                        token = ""
                elif char == "\n":
                    # end of line
                    if len(token)  > 0:
                        self.tokens.append(token)
                        # Don't have to reset... it will be done when starting the next line
                        self.tokens.append("\n")
                else:
                    # any other character
                    token += char

    def analyseFile(self, aFile):
        """
            Nothing yet
        """
        self.readTokens(aFile.readlines())
                    
    def getHeader(self):
        """
            Return the header of the result of one analysis
        """

if __name__ == "__main__":
    aFile = open(sys.argv[1])
    analyser = LilypondAnalyser()
    analyser.analyseFile(aFile)
    header = analyser.getHeader()
    if header == None:
        print "Piece has no header"
    else:
        print "Piece does have a header"

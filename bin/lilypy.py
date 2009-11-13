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

    def __init__(self, note, alter, index, duration):
        self.note = note
        self.alter = alter
        self.index = index
        self.duration = duration

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
        temp += "<" + str(self.duration) + ">"
        return temp

    def __repr__(self):
        return self.toString()


class LilypondHeader:

    def __init__(self):
        """
            Nothing yet
        """
        self.title = None

    def setTitle(self, title):
        self.title = title

    def toString(self):
        temp = "Header - ";
        if self.title == None:
            temp += "Title <unset>"
        else:
            temp += "Title: <" + self.title + ">"
        return temp

    def getHeaderFromTokens(self, tokens, openingIndex):
        """
            Get the content of the header. headerIndex specifies the position of the opening {
            Will return the position of the closing }
        """
        # analysing header
        tokenIndex = openingIndex + 1
        while tokenIndex < len(tokens):
            token = tokens[tokenIndex]
            if token != "\n":
                if token == "\\title":
                    # user wants to set the title
                    if tokens[tokenIndex + 1] == "=" and tokens[tokenIndex + 2] != "\n":
                        # all that's following is the title till the line closes
                        title = ""
                        tokenIndex += 2
                        while tokens[tokenIndex] != "\n":
                            if len(title) > 0:
                                title += " "
                            title += tokens[tokenIndex]
                            tokenIndex += 1
                        # Got to the end of the line
                        self.setTitle(title)
                    else:
                        raise Exception("Unexpected title definition")
                elif token == "}":
                    break
                else:
                    raise Exception("Unexpected token in header: " + token)
            tokenIndex+=1
        if tokenIndex >= len(tokens):
            raise Exception("Unexpected end of file")
        return tokenIndex # Closing } index
        

class LilypondStaff:
    """
        A Staff on a Lilypond script
    """

    def __init__(self):
        self.key = None
        self.cleff = None
        self.notes = []
        self.lastReferenceNote = None # When working with \relative
        self.lastDuration = 1 # Asume we start with a "Redonda"
        self.relative = False # Don't know how to read non relative parts, but anyway

    def readNote(self, token, absolute = False):
        """ Have to return a single note from a given token """
        note=token[0]
        if note == "a":
            note=MusicalNote.NOTE_A
        elif note == "b":
            note=MusicalNote.NOTE_B
        elif note == "c":
            note=MusicalNote.NOTE_C
        elif note == "d":
            note=MusicalNote.NOTE_D
        elif note == "e":
            note=MusicalNote.NOTE_E
        elif note == "f":
            note=MusicalNote.NOTE_F
        elif note == "g":
            note=MusicalNote.NOTE_G
        else:
            raise Exception("Unknown note: " + token[0])

        # TODO have to get the alteration.... but won't do it right now

        # Index, let's count the 's or ,s
        if absolute:
            index = 0
        else:
            index=self.lastReferenceNote.index;
            # TODO If it's relative, there are more calculations to make to know the index

        charIndex=1
        if charIndex < len(token):
            if token[charIndex] == ',':
                difference = -1
            elif token[charIndex] == '\'':
                difference = 1
        if difference != 0:
            while charIndex < len(token) and token[charIndex]:
                if token[charIndex] not in ",\'":
                    break; # finished
                if difference == -1 and token[charIndex] != ',' or difference == 1 and token[charIndex] != '\'':
                    raise Exception("Unexpected " + token[charIndex])
                index+=difference
                charIndex+=1

        # Got to the end of the index.... how about the duration?
        if charIndex >= len(token):
            # Got to the end of the note... have to use the previous duration
            return MusicalNote(note, 0, index, self.lastDuration)
        # One duration must follow
        
        
        

    def getStaffFromTokens(self, tokens, tokenIndex):
        """ Nothing yet """
        if tokens[tokenIndex+1] != '=':
            raise Exception("Unexpected Staff definition")
        if tokens[tokenIndex+2] != '\\relative':
            raise Exception("Don't know how to read non-relative staffs")
        # Let's read the relative note
        self.lastReferenceNote = self.readNote(tokens[tokenIndex+3], True)
        tokenIndex+=3
        
        return tokenIndex + 1

class LilypondAnalyser:

    def __init__(self):
        self.header = None
        self.tokens = []
        self.staffs = []

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
        nestedElements = []
        tokenIndex = -1
        while tokenIndex < len(self.tokens):
            tokenIndex+=1
            token = self.tokens[tokenIndex]
            if token == "\n":
                # Doesn't matter
                continue
            if token == "\\header":
                if self.header != None:
                    raise Exception("Header had already been set")
                if self.tokens[tokenIndex + 1] != '{':
                    raise Exception("Header definition is wrong")
                self.header = LilypondHeader()
                tokenIndex = self.header.getHeaderFromTokens(self.tokens, tokenIndex + 1) # from the opening { will return the closing }
            elif token == "\\new":
                # Is it one new staff?
                if self.tokens[tokenIndex+1] == "Staff":
                    # It's a new staff
                    staff = LilypondStaff()
                    # Let's read the staff
                    tokenIndex = staff.getStaffFromTokens(self.tokens, tokenIndex + 1) #Pass the opening Staff will return the closing }
                    self.staffs.append(staff)
            else:
                raise Exception("Unexpected " + token)


                    
    def getHeader(self):
        """
            Return the header of the result of one analysis
        """
        return self.header

if __name__ == "__main__":
    aFile = open(sys.argv[1])
    analyser = LilypondAnalyser()
    analyser.analyseFile(aFile)
    header = analyser.getHeader()
    if header == None:
        print "Piece has no header"
    else:
        print header.toString()

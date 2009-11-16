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

class LilypondToken:

    def __init__(self, word, line, pos):
        self.word = word
        self.line = line
        self.pos = pos

    def toString(self):
        return "Token: " + str(self.word) + " Line " + str(self.line) + " Pos " + str(self.pos)

    def raiseException(self, message = None):
        if message == None:
            raise Exception("Unexpected \"" + self.word + "\" on line " + str(self.line) + " pos " +  str(self.pos))
        else:
            raise Exception(str(message) + " on line " + str(self.line) + " pos " + str(self.pos))

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
            if token.word != "\n":
                if token.word == "title":
                    titleLine = token.line
                    # user wants to set the title
                    if tokens[tokenIndex + 1].word == "=":
                        # all that's following is the title till the line closes
                        title = ""
                        tokenIndex += 2
                        while tokens[tokenIndex].line == titleLine:
                            if len(title) > 0:
                                title += " "
                            title += tokens[tokenIndex].word
                            tokenIndex += 1
                        # Got to the end of the line
                        self.setTitle(title)
                        continue
                    else:
                        raise Exception("Unexpected title definition")
                elif token.word == "}":
                    break
                else:
                    token.raiseException()
            tokenIndex+=1
        if tokenIndex >= len(tokens):
            raise Exception("Unexpected end of file")
        return tokenIndex # Closing } index
        

class LilypondStaff:
    """
        A Staff on a Lilypond script
    """

    def __init__(self):
        self.cleff = None
        self.events = [] # Can be notes, chords, key changes
        self.lastReferenceNote = None # When working with \relative
        self.lastDuration = 1 # Asume we start with a "Redonda"
        self.relative = False # Don't know how to read non relative parts, but anyway

    def readNote(self, token, absolute = False):
        """ Have to return a single note from a given token """
        note=token.word[0]
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
            token.raiseException("Unknown note: " + token.word[0])

        # TODO have to get the alteration.... but won't do it right now
        alteration = 0
        charIndex = 1
        while charIndex + 2 <= len(token.word):
            # Could be altered
            alterText = token.word[charIndex:charIndex+2]
            if alterText not in ['is', 'es']:
                # Finished with the alterations
                break
            if alterText == 'is':
                # sharp
                alteration+=1
            else:
                alteration-=1
            charIndex+=2

        # Index, let's count the 's or ,s
        if absolute:
            index = 0
        else:
            index=self.lastReferenceNote.index;
            # TODO If it's relative, there are more calculations to make to know the index

        difference = 0
        if charIndex < len(token.word):
            if token.word[charIndex] == ',':
                difference = -1
            elif token.word[charIndex] == '\'':
                difference = 1
        if difference != 0:
            while charIndex < len(token.word) and token.word[charIndex]:
                if token.word[charIndex] not in ",\'":
                    break; # finished
                if difference == -1 and token.word[charIndex] != ',' or difference == 1 and token.word[charIndex] != '\'':
                    token[charIndex].raiseException()
                index+=difference
                charIndex+=1

        # Got to the end of the index.... how about the duration?
        if charIndex >= len(token.word):
            # Got to the end of the note... have to use the previous duration
            return MusicalNote(note, 0, index, self.lastDuration)
        # One duration must follow

    def getStaffKey(self, tokens, tokenIndex):
        """
            Get the key
        """
        noteStr = tokens[tokenIndex+1].word
        if noteStr[0] == 'a':
            note = MusicalNote.NOTE_A
        elif noteStr[0] == 'b':
            note = MusicalNote.NOTE_B
        elif noteStr[0] == 'c':
            note = MusicalNote.NOTE_C
        elif noteStr[0] == 'd':
            note = MusicalNote.NOTE_D
        elif noteStr[0] == 'e':
            note = MusicalNote.NOTE_E
        elif noteStr[0] == 'f':
            note = MusicalNote.NOTE_F
        elif noteStr[0] == 'g':
            note = MusicalNote.NOTE_G
        else:
            raise Exception("Unexpected note for staff key: " + noteStr)

        # Alterations?
        alteration = 0
        charIndex = 1
        while charIndex + 2 <= len(noteStr):
            alterStr = noteStr[charIndex:charIndex+2]
            if alterStr == 'es':
                alteration-=1
            elif alterStr == 'is':
                alteration+=1
            else:
                raise Exception('Unexpected alteration ' + alterStr)
            charIndex+=2

        majorStr = tokens[tokenIndex + 2].word
        if majorStr == '\\major':
            major = True
        elif majorStr == '\\minor':
            major = False
        else:
            raise Exception("Unexpected tonality definition: " + majorStr)

        self.events.append(MusicalKey(note, alteration, major))
        return tokenIndex + 2
        
    def getStaffFromTokens(self, tokens, tokenIndex):
        """ Nothing yet """
        if tokens[tokenIndex+1].word != '\\relative':
            raise Exception("Don't know how to read non-relative staffs")
        # Let's read the relative note
        self.lastReferenceNote = self.readNote(tokens[tokenIndex+2], True)

        # Now a { must come
        if tokens[tokenIndex+3].word != "{":
            tokens[tokenIndex + 3].raiseException("Unexpected staff opening");

        # Now we start processing the things that come inside of the staff
        tokenIndex+=4
        while True:
            token = tokens[tokenIndex]
            if token.word == '}':
                # Closing staff
                break
            if token.word == '\\clef':
                # setting the key
                tokenIndex += 1
            elif token.word == '\\key':
                tokenIndex = self.getStaffKey(tokens, tokenIndex)
            elif token.word == '\\time':
                tokenIndex += 1
            else:
                print "Token inside of staff" + token.toString()

            tokenIndex += 1
        
        return tokenIndex

class LilypondAnalyser:

    def __init__(self):
        self.header = None
        self.version = None
        self.tokens = []
        self.staffs = []

    def readTokens(self, lines):
        lineCounter = 1
        for line in lines:
            lineCounter += 1
            token = "" # Starting a line, word is empty
            posCounter=0
            for char in line:
                posCounter+=1
                if char == " " or char == "\t":
                    # space or tab
                    if len(token) > 0:
                        # there is something in the token
                        self.tokens.append(LilypondToken(token, lineCounter, posCounter - len(token)))
                        token = ""
                elif char == "\n":
                    # end of line
                    if len(token) > 0:
                        self.tokens.append(LilypondToken(token, lineCounter, posCounter - len(token)))
                        # Don't have to reset... it will be done when starting the next line
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
        while tokenIndex+1 < len(self.tokens):
            tokenIndex+=1
            token = self.tokens[tokenIndex]
            if token.word == "\n":
                # Doesn't matter
                continue
            if token.word == "\\header":
                if self.header != None:
                    raise Exception("Header had already been set")
                if self.tokens[tokenIndex + 1].word != '{':
                    raise Exception("Header definition is wrong")
                self.header = LilypondHeader()
                tokenIndex = self.header.getHeaderFromTokens(self.tokens, tokenIndex + 1) # from the opening { will return the closing }
            elif token.word == "\\version":
                # Lilypond version
                self.version = self.tokens[tokenIndex+1].word.rstrip("\"").lstrip("\"")
                tokenIndex+=1
            elif token.word == "\\new":
                # Is it one new staff?
                if self.tokens[tokenIndex+1].word == "Staff":
                    # It's a new staff
                    staff = LilypondStaff()
                    # Let's read the staff
                    tokenIndex = staff.getStaffFromTokens(self.tokens, tokenIndex + 1) #Pass the opening Staff will return the closing }
                    self.staffs.append(staff)
            else:
                token.raiseException()


                    
    def getHeader(self):
        """
            Return the header of the result of one analysis
        """
        return self.header

    def getLilypondVersion(self):
        return self.version

if __name__ == "__main__":
    aFile = open(sys.argv[1])
    analyser = LilypondAnalyser()
    analyser.analyseFile(aFile)
    header = analyser.getHeader()
    if header == None:
        print "Piece has no header"
    else:
        print header.toString()
    lilypondVersion=analyser.getLilypondVersion()
    if lilypondVersion == None:
        print "Lilypond version: not especified"
    else:
        print "Lilypond version: " + lilypondVersion

    print "Staffs:"
    for staff in analyser.staffs:
        print "\tStaff"
        for event in staff.events:
            print "\t\t" + event.toString()

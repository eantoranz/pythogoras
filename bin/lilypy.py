#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2009 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

import sys
from Music import *

class LilypondTie:
    """ Note tied to anoher (usually written as ~ )"""
    
    def __init__(self):
        # nothing to do
        None
    
    def toString(self):
        return "Lilypond Tie";

class LilypondToken:

    def __init__(self, word, line, pos):
        self.word = word
        self.line = line
        self.pos = pos

    def toString(self):
        return "Token: " + str(self.word) + " Line " + str(self.line) + " Pos " + str(self.pos)
    
    def __str__(self):
        return self.toString()

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
    
    def __str__(self):
        return self.toString()

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
        

class LilypondTimeMarker:

    def __init__(self, numerator = None, denominator = None):
        self.numerator = numerator
        self.denominator = denominator

    def readFromToken(self, token):
        pos = token.word.find('/')
        if pos == -1:
            raise Exception("Invalid time marker: " + token.toString())
        self.numerator = int(token.word[0:pos])
        self.denominator = int(token.word[pos+1:])

    def toString(self):
        return "Time Marker: " + str(self.numerator) + "/" + str(self.denominator)

class LilypondStaff:
    """
        A Staff on a Lilypond script
    """

    def __init__(self):
        self.cleff = None
        self.events = [] # Can be notes, chords, polyphonies, key changes
        self.lastReferenceNote = None # When working with \relative
        self.lastDuration = None # Has to be separate from the previous note because there are rests and they can't be used to calculate indexes
        self.lastDots = 0 # same thing of lastDuration
        self.relative = False # Don't know how to read non relative parts, but anyway

        self.firstTimeMarker = None
        self.firstKey = None # First key of the staff
        self.times = None

    def getFirstTimeMarker(self):
        if self.firstTimeMarker == None:
            return LilypondTimeMarker(4, 4)
        return self.firstTimeMarker

    def getFirstKey(self):
        if self.firstKey == None:
            return MusicalKey(MusicalNote.NOTE_C, 0, True) # return C major
        return self.firstKey

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

        event = MusicalKey(note, alteration, major)
        if self.firstKey == None:
            self.firstKey = event
        self.events.append(event)
        return tokenIndex + 2

    def getMusicalEvent(self, tokens, tokenIndex):
        """
            Get a musical event (a single note, polyphonic voice or a chord)
        """

        token = tokens[tokenIndex].word
        if token == '<':
            # It's a chord
            return self.getChord(tokens, tokenIndex) # Will return the position of the closing >
        elif token == "<<":
            # it's a polyphonic voice
            return self.getPolyphony(tokens, tokenIndex) # Will return the position of the closing >>
        elif token == "~":
            # it's a tie
            self.events.append(LilypondTie())
            return tokenIndex
        else:
            # It's a single note
            note = self.getNote(tokens[tokenIndex], self.lastReferenceNote, self.lastDuration, self.lastDots)
            if note.note not in [ 0, None]:
                # it's not a rest
                self.lastReferenceNote = note
            self.lastDuration = note.duration
            self.lastDots = note.dots
            self.events.append(note)
            #DEBUG Message sys.stderr.write("Created a note: " + note.toString() + "\n")

        return tokenIndex # return the same token index

    def getNoteIndex(self, note, index, previousNote):
        # if previous note == None, will return the provided index
        if previousNote == None:
            return index

        # When in relative mode, when a note is read, the note's index (default) is calculated based on that it's within a fouth of the
        # previous note
        if previousNote.note == note:
            return index + previousNote.index
        # Notes are different
        distance = previousNote.getDistance(MusicalNote(note, 0, previousNote.index))
        # Distance to the note with the same index of the previous note
        distance = distance[0] # Only care about diatonic semitones
        if distance < 0:
            distance += 7
        if distance > 3:
            # The note is within a fourth going down
            if previousNote.note == MusicalNote.NOTE_C:
                return previousNote.index - 1 + index
            if previousNote.note == MusicalNote.NOTE_D:
                if note == MusicalNote.NOTE_C:
                    return previousNote.index + index
                return previousNote.index - 1 + index
            if previousNote.note == MusicalNote.NOTE_E:
                if note in [MusicalNote.NOTE_C, MusicalNote.NOTE_D]:
                    return previousNote.index + index
                return previousNote.index - 1 + index
            # F G A B
            return previousNote.index + index
        elif distance > 0:
            # The note is within a fourth going up
            if previousNote.note == MusicalNote.NOTE_B:
                return previousNote.index + 1 + index
            if previousNote.note == MusicalNote.NOTE_A:
                if note == MusicalNote.NOTE_B:
                    return previousNote.index + index
                return previousNote.index + 1 + index
            if previousNote.note == MusicalNote.NOTE_G:
                if note in [MusicalNote.NOTE_A, MusicalNote.NOTE_B]:
                    return previousNote.index + index
                return previousNote.index + 1 + index
            # C D E F
            return previousNote.index + index
                
        else:
            raise Exception("Shouldn't find a distance of " + str(distance) + " at this point")

    def getNote(self, token, previousNote, previousDuration = None, previousDots = 0, includeDuration = True):
        """
            Get a note from the staff
        """
        noteStr = token.word
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
        elif noteStr[0] == 'r':
            # Rest
            note = None
        else:
            raise Exception("Unexpected note definition: " + token.toString())

        alteration = 0
        charIndex = 1
        if note != None:
            while charIndex + 2 <= len(noteStr):
                # Could have an alteration
                alterStr = noteStr[charIndex:charIndex+2]
                if alterStr == 'es':
                    alteration -= 1
                elif alterStr == 'is':
                    alteration += 1
                else:
                    # Not an alteration
                    break
                charIndex += 2
        
        index = 0
        duration = None # Just in case
        dots = 0
        while charIndex < len(noteStr):
            if noteStr[charIndex] == '\'':
                index+=1
            elif noteStr[charIndex] == ',':
                index-=1
            else:
                # Only the duration and possibly dots are left
                if not includeDuration:
                    raise Exception("Unexpected note duration: " + token.toString())
                # duration is coming next
                durationStr = ""
                durationIndexStart = charIndex # char index where the duration _possibly_ begins
                while charIndex < len(noteStr) and noteStr[charIndex] in '0123456789':
                    charIndex += 1
                duration = noteStr[durationIndexStart:charIndex]
                # is there a dot present?
                if charIndex < len(noteStr):
                    # could be dotted
                    dots = 0
                    while charIndex < len(noteStr) and noteStr[charIndex]:
                        dots += 1
                        charIndex += 1
                break
            charIndex+=1

        if includeDuration and duration == None:
            if previousDuration == None:
                duration = 4 # it's a black by defect
            else:
                duration = previousDuration
            dots = previousDots
        
        if previousNote == None:
            index = index + 3
        elif note == None:
            # It's a rest
            return MusicalNote(0, 0, previousNote.index, duration, dots)
        else:
            index = self.getNoteIndex(note, index, previousNote)

        if includeDuration:
            return MusicalNote(note, alteration, index, duration, dots, self.times)
        else:
            return MusicalNote(note, alteration, index)
        

    def getChord(self, tokens, tokenIndex):
        if tokens[tokenIndex].word != '<':
            raise Exception("Found an unexpected chord starter: " + str(tokens[tokenIndex]))
        # Have to get the notes till we find a chord closer (>)
        notes = []
        tokenIndex += 1
        previousNote = self.lastReferenceNote
        while True:
            token = tokens[tokenIndex]
            if token.word[0] == '>':
                # Closing chord....
                if len(notes) > 0:
                    # Does the chord have a duration?
                    if len(token.word) > 1:
                        duration = token.word[1:]
                    else:
                        duration = self.lastDuration
                    self.events.append(MusicalChord(notes, duration))
                    self.lastReferenceNote = notes[0]
                
                # @TODO this is where we go out... maybe we chould rewrite the function to get he return at the end
                self.lastDuration = duration
                self.lastDots = True
                return tokenIndex
            
            # add a new note
            note = self.getNote(tokens[tokenIndex], previousNote, None, None, False)
            previousNote = note # For the calculation of the next node
            notes.append(note)
            tokenIndex+=1 #next token
    
    def getPolyphony(self, tokens, tokenIndex):
        if tokens[tokenIndex].word != '<<':
            raise Exception("Found an unexpected polyphony starter: " + str(tokens[tokenIndex]))
    
        tokenIndex += 1
        # have to find the voices
        voices = list()
        while tokens[tokenIndex].word != ">>":
            # it should be the start of a voice
            if tokens[tokenIndex].word != "{":
                raise Exception("Found an unexpected polyphonic voice starter: " + str(tokens[tokenIndex]))
            # have to go on finding notes to create a voice
            tokenIndex += 1
            #@TODO do I have to use different reference notes for notes, chords and polyphonies?
            notes = list()
            while tokens[tokenIndex].word != "}":
                # let's get the notes
                note = self.getNote(tokens[tokenIndex], self.lastReferenceNote, self.lastDuration, self.lastDotted, True)
                notes.append(note)
                if note.note not in [0, None]:
                    # it's not a rest
                    self.lastReferenceNote = note
                self.lastDuration = note.duration
                self.lastDots = note.dots
                tokenIndex += 1
            # end of a voice
            voices.append(notes)
            
            # do we have more voices?
            tokenIndex += 1
            if tokens[tokenIndex].word == "\\\\":
                # we have another voice
                tokenIndex += 1
        # reached the end of the polyphony
        self.events.append(MusicalPolyphony(voices))
        
        return tokenIndex

    def getTimeMarker(self, token):
        timeMarker = LilypondTimeMarker()
        if self.firstTimeMarker == None:
            self.firstTimeMarker = timeMarker
        timeMarker.readFromToken(token)
        self.events.append(timeMarker)

    def getStaffFromTokens(self, tokens, tokenIndex):
        """ Nothing yet """
        if tokens[tokenIndex+1].word != '\\relative':
            raise Exception("Don't know how to read non-relative staffs")
        # Let's read the relative note
        self.lastReferenceNote = self.getNote(tokens[tokenIndex+2], None, None, None, False)
        # Set duration to blacks by default
        self.lastReferenceNote.duration='4'

        # Now a { must come
        if tokens[tokenIndex + 3].word != "{":
            tokens[tokenIndex + 3].raiseException("Unexpected staff opening");

        # Now we start processing the things that come inside of the staff
        tokenIndex+=4
        while True:
            token = tokens[tokenIndex].word
            if token == '}':
                if self.times == None:
                    # Closing staff
                    break
                # probably closing a times
                self.times = None
            elif token == '\\clef':
                # setting the key
                tokenIndex += 1
            elif token == '\\key':
                tokenIndex = self.getStaffKey(tokens, tokenIndex)
            elif token == '\\time':
                self.getTimeMarker(tokens[tokenIndex+1])
                tokenIndex += 1
            elif token == '\\bar':
                tokenIndex += 1 # Just a bar
            elif token == "\\times":
                # adjustment in measurement
                tokenIndex += 1
                # this has to be now a division
                pos = tokens[tokenIndex].word.find("/")
                if not pos:
                    raise Exception("Times has to have a x/y format")
                numerator = int(tokens[tokenIndex].word[:pos])
                denominator = int(tokens[tokenIndex].word[pos+1:])
                self.times = float(denominator) / numerator
                # now a { must follow
                tokenIndex += 1
                if tokens[tokenIndex].word != "{":
                    raise Exception("Times has to start with a {")
            else:
                # It must be a musical event
                tokenIndex = self.getMusicalEvent(tokens, tokenIndex)

            tokenIndex += 1
        
        return tokenIndex

class LilypondSystem:
    """
        A system is made of various staffs
    """

    def __init__(self):
        self.staffs = []

    def readSystemFromTokens(self, tokens, tokenIndex):
        """
            read the system from the tokens provided. tokenIndex especifyes the <<... have to return the closing >> index
        """

        if tokens[tokenIndex].word != "<<":
            raise Exception("Wrong system starter: " + tokens[tokenIndex].toString() + ". Expecting <<")

        tokenIndex = tokenIndex+1
        while True:
            token = tokens[tokenIndex]
            if token.word == ">>":
                # closing system
                return tokenIndex
            if token.word == "\\new":
                if tokens[tokenIndex+1].word == "Staff":
                    staff = LilypondStaff()
                    tokenIndex = staff.getStaffFromTokens(tokens, tokenIndex + 1)
                    self.staffs.append(staff)
                else:
                    raise Exception("Unexpected new instance in system: " + tokens[tokenIndex+1].toString())
            else:
                raise Exception("Unexpected system member: " + token.toString())
            tokenIndex+=1
                

class LilypondAnalyser:

    def __init__(self):
        self.header = None
        self.version = None
        self.tokens = []
        self.systems = []
        self.staffs = []

    def readTokens(self, lines):
        lineCounter = 1
        for line in lines:
            lineCounter += 1
            token = "" # Starting a line, word is empty
            posCounter=0
            comment = False
            for char in line:
                if comment:
                    continue
                posCounter+=1
                if char == " " or char == "\t":
                    # space or tab
                    if len(token) > 0:
                        # there is something in the token
                        if token[0] == '%':
                            comment = True
                            token = ""
                            continue
                        self.tokens.append(LilypondToken(token, lineCounter, posCounter - len(token)))
                        token = ""
                elif char == "\n":
                    # end of line
                    if len(token) > 0:
                        if token[0] == '%':
                            # nevermind what the line says from now on
                            comment = True
                            token = ""
                            continue
                        self.tokens.append(LilypondToken(token, lineCounter, posCounter - len(token)))
                        # Don't have to reset... it will be done when starting the next line
                        token = ""
                else:
                    # any other character
                    token += char
            if len(token) != 0:
                self.tokens.append(LilypondToken(token, lineCounter, posCounter - len(token)))


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
            elif token.word == "<<":
                # System starter
                lilypondSystem = LilypondSystem()
                tokenIndex = lilypondSystem.readSystemFromTokens(self.tokens, tokenIndex)
                self.systems.append(lilypondSystem)
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

    systems = analyser.systems
    if len(systems) > 0:
        print "Systems: "
        for aSystem in systems:
            print "\tSystem"
            for staff in aSystem.staffs:
                print "\t\tStaff"
                for event in staff.events:
                    print "\t\t\t" + event.toString()
    staffs = analyser.staffs
    if len(staffs) > 0:
        print "Staffs:"
        for staff in analyser.staffs:
            print "\tStaff"
            for event in staff.events:
                print "\t\t" + event.toString()

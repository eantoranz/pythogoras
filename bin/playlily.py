#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright 2009 Edmundo Carmona Antoranz
Released under the terms of the Affero GPLv3
"""

import lilypy
from Music import *
from Wave import Wave
from WavePlayer import WavePlayer
import sys
import math

class LilypondNotePlayer:

    def __init__(self, beatsPerMinute, beatUnit, tuningSystem, note, samplingRate = 44100):
        self.note = note
        self.volume = 1 # Full colume for starters
        # How many samples will I have to play?
        self.totalSamples = int(beatUnit * samplingRate * 60 / (note.duration * beatsPerMinute))
        if note.dotted:
            self.totalSamples *= 1.5
        self.frequency = tuningSystem.getFrequency(note)
        self.wave = Wave(tuningSystem.getFrequency(note), samplingRate)
        self.counter = 0
    
    def getNextValue(self):
        self.counter+=1
        return self.wave.getNextValue()

    def finished(self):
        return self.counter >= self.totalSamples
        
class LilypondChordPlayer:

    def __init__(self, beatsPerMinute, beatUnit, tuningSystem, chord, samplingRate = 44100):
        """
            A chord player
        """
        # Create a number of note players and that's it
        self.players = []
        for note in chord.notes:
            self.players.append(LilypondNotePlayer(beatsPerMinute, beatUnit, tuningSystem, note, samplingRate))
        self.length = len(self.players)

    def getNextValue(self):
        accumulator = 0
        for player in self.players:
            accumulator += player.getNextValue()
        return int(accumulator / self.length)

    def finished(self):
        return self.players[0].finished()

class LilypondStaffPlayer:

    def __init__(self, beatsPerMinute, tuningSystem, samplingRate = 44100):
        """
            A Staff Player
        """
        self.beatsPerMinute = beatsPerMinute
        self.beatUnit = None # Will be caught from staff
        self.tuningSystem = tuningSystem
        self.samplingRate = samplingRate

        self.staff = None
        self.eventPlayer = None # Nothing is being played right now
        self.eventCounterIndex = -1

        self.finished = False

    def playStaff(self, staff):
        self.staff = staff
        # Time Marker
        self.beatUnit = self.staff.getFirstTimeMarker().denominator

    def getNextValue(self):
        if self.eventPlayer == None:
            # What's the next event?
            while True:
                self.eventCounterIndex+=1
                if self.eventCounterIndex < len(self.staff.events):
                    self.event = self.staff.events[self.eventCounterIndex]
                    if isinstance(self.event, MusicalNote):
                        self.eventPlayer = LilypondNotePlayer(self.beatsPerMinute, self.beatUnit, self.tuningSystem, self.event, self.samplingRate)
                        break
                    elif isinstance(self.event, MusicalChord):
                        self.eventPlayer = LilypondChordPlayer(self.beatsPerMinute, self.beatUnit, self.tuningSystem, self.event, self.samplingRate)
                        break
                else:
                    break
            if self.eventCounterIndex >= len(self.staff.events):
                # Finished
               self.finished = True
               return 0
        temp = self.eventPlayer.getNextValue()
        if self.eventPlayer.finished():
            self.eventPlayer = None # Have to get the next event
        return temp

class LilypondSystemPlayer:
    """
        Class that can play a system instead of just a staff
    """

    def __init__(self, beatsPerMinute, tuningSystem, samplingRate = 44100):
        self.beatsPerMinute = beatsPerMinute
        self.tuningSystem = tuningSystem
        self.samplingRate = samplingRate


class LilypondPlayer:
    """
        Class that can play from a staff or a system
    """

    def __init__(self, beatsPerMinute, tuningSystem, wavePlayer):
        self.beatsPerMinute = beatsPerMinute
        self.wavePlayer = wavePlayer
        self.tuningSystem = tuningSystem
        self.samplingRate = wavePlayer.samplingRate

    def playSystem(self, tuningSystem, lilypondSystem):
        """
            play from a lilypond system
        """
        sys.stderr.write("Playing Lilypond system\n")

    def playStaff(self, staff):
        """
            Play from a staff
        """
        player = LilypondStaffPlayer(self.beatsPerMinute, self.tuningSystem, self.samplingRate)
        player.playStaff(staff)
        while not player.finished:
            self.wavePlayer.play(player.getNextValue())
        sys.stderr.write("Finished playing\n")
        sys.stderr.flush()
        # Finished playing
        

def main(argv):
    argc = len(argv)
    if (argc == 1):
        sys.stderr.write("In order to play a file, you have to provide the speed at which a measurement unit will be played (in beats per minute).\n")
        sys.stderr.write("Then you can provide the system you want to use to play it\n")
        sys.stderr.write("Pythagorean: specify a p and optionally the base frequency of A4\n")
        sys.stderr.write("\tEx: playmidi.py p 442 lilypond-file.ly\n")
        sys.stderr.write("Just system: specify a j and the key to use (only major keys, so if it's B minor set it to F).\n")
        sys.stderr.write("\tOptionally set the base freq of the base note of the key\n")
        sys.stderr.write("\tEx: playmidi.py j Bb lilypond-file.ly\n")
        sys.stderr.write("\tEx: playmidi.py j A 442 lilypond-file.ly\n")
        sys.stderr.write("If you want to use tempered system, don't specify anything. Optionally the freq of A4\n")
        sys.stderr.write("\tEx: playmidi.py 441 lilypond-file.ly\n")
        sys.stderr.flush()
        sys.exit(1)

    speed = int(argv[1])
    system = None
    fileName = None

    if argv[2] == "p":
        system = argv
        # pythagorean
        # was the frequency for A4 specified?
        baseFreq = 440
        try:
            baseFreq = int(argv[3])
            if argc >= 3:
                fileName = argv[4]
        except:
            # probably frequency wasn't provided
            fileName = argv[3]
        # Let's create the tuning system
        system = PythagoreanSystem(baseFreq)
    elif argv[2] == "j":
        # Just.... have to provide the key note
        keyNoteStr = argv[3].lower()
        keyNote = None
        alteration = 0
        if keyNoteStr[0] == "a":
            keyNote = MusicalNote.NOTE_A
        elif keyNoteStr[0] == "b":
            keyNote = MusicalNote.NOTE_B
        elif keyNoteStr[0] == "c":
            keyNote = MusicalNote.NOTE_C
        elif keyNoteStr[0] == "d":
            keyNote = MusicalNote.NOTE_D
        elif keyNoteStr[0] == "e":
            keyNote = MusicalNote.NOTE_E
        elif keyNoteStr[0] == "f":
            keyNote = MusicalNote.NOTE_F
        elif keyNoteStr[0] == "g":
            keyNote = MusicalNote.NOTE_G
        if keyNote == None:
            sys.stderr.write("Didn't provide a valid base key note\n")
            sys.exit(1)
        if len(keyNoteStr) > 1:
            # Also we have an alteration
            alterChar = keyNoteStr[1]
            difference = 0
            if alterChar == 'b':
                difference = -1
            elif alterChar == '#':
                difference = 1
            else:
                sys.stderr.write("Invalid alteration char. Use b or #\n")
                sys.exit(1)
            i = 1
            while i < len(keyNoteStr):
                if keyNoteStr[i] != alterChar:
                    sys.stderr.write("Changed alteration char at index " + str(i + 1) + "\n")
                    sys.exit(1)
                alteration += difference
                i+=1
        system = JustSystem(keyNote, alteration)
        fileName = argv[4]
    else:
        # Tempered System
        try:
            baseFreq = int(argv[2])
            system = TemperedSystem(baseFreq)
            fileName = argv[3]
        except:
            system = TemperedSystem.getInstance()
            fileName = argv[2]

    if fileName == None:
        sys.stderr.write("Didn't provide any file name to play\n")
        sys.stderr.flush()
        sys.exit(1)
    
    sys.stderr.write("reading file " + fileName + "\n")
    
    # Create a lilypond analyser
    analyser = lilypy.LilypondAnalyser()
    analyser.analyseFile(file(fileName))
    sys.stderr.write("Finished analyzing file\n")

    lilyPlayer = LilypondPlayer(speed, system, WavePlayer(11025))
    systems = analyser.systems
    if len(systems) > 0:
        # Have to play the systems
        for system in systems:
            lilyPlayer.playSystem(system)
        sys.exit(0)
    # No systems.... let's check staffs
    staffs = analyser.staffs
    if len(staffs) > 0:
        for staff in staffs:
            lilyPlayer.playStaff(staff)
        sys.exit(0)
    sys.stderr.write("No lilypond systems or staffs to play")
    sys.exit(-1)

if __name__ == "__main__":
    main(sys.argv)

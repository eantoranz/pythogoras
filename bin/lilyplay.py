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
        self.samplingRate = samplingRate
        # How many samples will I have to play?
        self.totalSamples = int(beatUnit * samplingRate * 60 / (note.duration * beatsPerMinute))
        if note.dotted:
            self.totalSamples *= 1.5
        self.frequency = tuningSystem.getFrequency(note)
        self.wave = Wave(tuningSystem.getFrequency(note), samplingRate)
        self.counter = 0
        self.volumeRate = None
    
    def getNextValue(self):
        self.counter+=1

        # Do we have to lower the volume?
        if self.volumeRate == None:
            if self.totalSamples - self.counter <= self.samplingRate * 0.05:
                # Have to calculate a volume rate
                self.volumeRate = math.exp(math.log(0.01) / (self.totalSamples -  self.counter))
        if self.volumeRate != None:
            self.wave.setVolume(self.volume * self.volumeRate)

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

    def __init__(self, beatsPerMinute, tuningSystem, staff, samplingRate = 44100):
        """
            A Staff Player
        """
        self.beatsPerMinute = beatsPerMinute
        self.staff = staff
        # beat unit from Time Marker
        self.beatUnit = self.staff.getFirstTimeMarker().denominator
        self.tuningSystem = tuningSystem
        self.samplingRate = samplingRate

        self.eventPlayer = None # Nothing is being played right now
        self.eventCounterIndex = -1

        self.finished = False

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
                    elif isinstance(self.event, MusicalKey):
                        # If it's just system, have to change it
                        if isinstance(self.tuningSystem, JustSystem):
                            # Frequency of the new base note under the actual tuning system
                            newBaseNote = MusicalNote(self.event.note, self.event.alteration, 4)
                            newBaseFreq = self.tuningSystem.getFrequency(newBaseNote)
                            sys.stderr.write("Modulating to " + newBaseNote.toString() + " set to " + str(newBaseFreq) + "\n")
                            self.tuningSystem = JustSystem(self.event.note, self.event.alteration, newBaseFreq)
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

    def __init__(self, beatsPerMinute, tuningSystem, system, samplingRate = 44100):
        self.players = []
        for staff in system.staffs:
            self.players.append(LilypondStaffPlayer(beatsPerMinute, tuningSystem, staff, samplingRate))
        self.length = len(self.players)

    def getNextValue(self):
        accumulator = 0
        for player in self.players:
            if player.finished:
                self.players.remove(player)
                self.length -= 1
                continue
            accumulator += player.getNextValue()
        if self.length == 0:
            return 0
        return int(accumulator / self.length)

    def isFinished(self):
        return self.length <= 0


class LilypondPlayer:
    """
        Class that can play from a staff or a system
    """

    SYSTEM_EQUAL_TEMPERED = 1
    SYSTEM_PYTHAGOREAN = 2
    SYSTEM_JUST = 3

    def __init__(self, beatsPerMinute, tuningSystem, baseFreq, wavePlayer):
        self.beatsPerMinute = beatsPerMinute
        self.wavePlayer = wavePlayer
        self.tuningSystem = tuningSystem
        self.baseFreq = baseFreq
        self.samplingRate = wavePlayer.samplingRate

    def playSystem(self, system):
        """
            play from a lilypond system
        """
        player = None
        if self.tuningSystem == LilypondPlayer.SYSTEM_EQUAL_TEMPERED:
            if self.baseFreq == None:
                self.baseFreq = TuningSystem.FREQ_A4
            player = LilypondSystemPlayer(self.beatsPerMinute, TemperedSystem(self.baseFreq), system, self.samplingRate)
        elif self.tuningSystem == LilypondPlayer.SYSTEM_PYTHAGOREAN:
            if self.baseFreq == None:
                self.baseFreq = TuningSystem.FREQ_A4
            player = LilypondSystemPlayer(self.beatsPerMinute, PythagoreanSystem(self.baseFreq), system, self.samplingRate)
        elif self.tuningSystem == LilypondPlayer.SYSTEM_JUST:
            key = system.staffs[0].getFirstKey()
            player = LilypondSystemPlayer(self.beatsPerMinute, JustSystem(key.note, key.alteration, self.baseFreq), system, self.samplingRate)
        else:
            sys.stderr.write("Don't know what tuning system to use to play lilypond file\n")
            sys.stderr.flush()
            sys.exit(1)

        while not player.isFinished():
            self.wavePlayer.play(player.getNextValue())
        sys.stderr.write("Finished playing system\n")
        sys.stderr.flush()
        # finished playing

    def playStaff(self, staff):
        """
            Play from a staff
        """
        player = None
        if self.tuningSystem == LilypondPlayer.SYSTEM_EQUAL_TEMPERED:
            if self.baseFreq == None:
                self.baseFreq = TuningSystem.FREQ_A4
            player = LilypondStaffPlayer(self.beatsPerMinute, TemperedSystem(self.baseFreq), staff, self.samplingRate)
        elif self.tuningSystem == LilypondPlayer.SYSTEM_PYTHAGOREAN:
            if self.baseFreq == None:
                self.baseFreq = TuningSystem.FREQ_A4
            player = LilypondStaffPlayer(self.beatsPerMinute, PythagoreanSystem(self.baseFreq), staff, self.samplingRate)
        elif self.tuningSystem == LilypondPlayer.SYSTEM_JUST:
            key = staff.getFirstKey()
            player = LilypondStaffPlayer(self.beatsPerMinute, JustSystem(key.note, key.alteration, self.baseFreq), staff, self.samplingRate)
        else:
            sys.stderr.write("Don't know what tuning system to use to play lilypond file\n")
            sys.stderr.flush()
            sys.exit(1)
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
        sys.stderr.write("\tEx: lilyplay.py p 442 lilypond-file.ly\n")
        sys.stderr.write("Just system: specify a j and the key to use (only major keys, so if it's B minor set it to F).\n")
        sys.stderr.write("\tOptionally set the base freq of the base note of the key\n")
        sys.stderr.write("\tEx: lilyplay.py j Bb lilypond-file.ly\n")
        sys.stderr.write("\tEx: lilyplay.py j A 442 lilypond-file.ly\n")
        sys.stderr.write("If you want to use tempered system, don't specify anything. Optionally the freq of A4\n")
        sys.stderr.write("\tEx: lilyplay.py 441 lilypond-file.ly\n")
        sys.stderr.write("\n")
        sys.stderr.write("As a last argument, can provide a filename where the raw data can be output to (if - is specified, standard output is used)\n")
        sys.stderr.write("\n")
        sys.stderr.write("Output will be raw stereo, 11.25 Khtz, Little Endian, 16-bit per channel\n")
        sys.stderr.flush()
        sys.exit(1)

    speed = int(argv[1])
    system = None
    baseFreq = None
    inputFile = None
    outputFile = None

    if argv[2] == "p":
        system = argv
        # pythagorean
        # Let's create the tuning system
        system = LilypondPlayer.SYSTEM_PYTHAGOREAN
        # was the frequency for A4 specified?
        baseFreq = 440
        try:
            baseFreq = int(argv[3])
            if argc >= 3:
                inputFile = argv[4]
                try:
                    outputFile = argv[5]
                except:
                    None
        except:
            # probably frequency wasn't provided
            inputFile = argv[3]
            try:
                outputFile = argv[4]
            except:
                None
    elif argv[2] == "j":
        # Just.... have to provide the key note
        system = LilypondPlayer.SYSTEM_JUST
        try:
            baseFreq = int(argv[3])
            inputFile = argv[4]
            outputFile = argv[5]
        except:
            inputFile = argv[3]
            try:
                outputFile = argv[4]
            except:
                None
    else:
        # Tempered System
        system = LilypondPlayer.SYSTEM_EQUAL_TEMPERED
        try:
            baseFreq = int(argv[2])
            inputFile = argv[3]
            try:
                outputFile = argv[4]
            except:
                None
        except:
            inputFile = argv[2]
            try:
                outputFile = argv[3]
            except:
                None

    if inputFile == None:
        sys.stderr.write("Didn't provide any file name to play\n")
        sys.stderr.flush()
        sys.exit(1)
    
    if outputFile != None:
        if outputFile == '-':
            outputFile = sys.stdout
        else:
            # The user asked to write on a real file
            outputFile = open(outputFile, 'w')
    
    sys.stderr.write("reading file " + inputFile + "\n")
    
    # Create a lilypond analyser
    analyser = lilypy.LilypondAnalyser()
    analyser.analyseFile(file(inputFile))
    sys.stderr.write("Finished analyzing file\n")

    lilyPlayer = LilypondPlayer(speed, system, baseFreq, WavePlayer(11025, outputFile))
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

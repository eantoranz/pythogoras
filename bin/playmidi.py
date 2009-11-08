#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright 2009 Edmundo Carmona Antoranz
Released under the terms of the Affero GPLv3
"""

from midi import *
from Music import *
from Wave import Wave
from WavePlayer import WavePlayer
import sys

class EventListNode:
    """
    List of events taking place at a moment in time
    """
    def __init__(self, time):
        self.time = time
        self.events=[]
        self.nextNode = None

    def addEvent(self, event):
        self.events.append(event)

    def getDuration(self):
        if self.nextNode == None:
            return None
        return self.nextNode.time - self.time

class EventList:
    """
    List of events ordered by time
    """
    def __init__(self):
        self.firstNode = None
        self.trackNumber = 0 # number of tracks

    def addEvent(self, event):
        if event.type == "DeltaTime":
            # nothing to do with that
            return
        eventTime = event.time
        node = self.firstNode
        previous = None

        while node != None and node.time < eventTime:
            previous = node
            node = node.nextNode

        if node == None:
            # got to the end of the list
            node = EventListNode(eventTime)
            if previous != None:
                # Have to place the node at the end of the list (last node = previous)
                previous.nextNode = node
            else:
                # First event of the list
                self.firstNode = node
        elif node.time > eventTime:
            # have to place a node between node and previous
            newNode = EventListNode(eventTime)
            previous.nextNode = newNode
            newNode.nextNode = node
            node = newNode
        else:
            # found a node for the given time
            None
        node.addEvent(event)
        # Number of tracks
        if event.track.index > self.trackNumber:
            self.trackNumber = event.track.index

    def printEvents(self):
        node = self.firstNode
        while node != None:
            sys.stderr.write("Time: " + str(node.time) + "\n")
            for event in node.events:
                sys.stderr.write("\t" + str(event) + "\n")
            node = node.nextNode

class TrackPlayer:
    """
    Will play a note that's provided to it
    """

    def __init__(self, system):
        self.system = system
        self.wave = None

    def play(self, musicalNote):
        if musicalNote == None:
            self.mute()
        else:
            self.wave = Wave(self.system.getFrequency(musicalNote))

    def mute(self):
        self.wave = None

    def getNextValue(self):
        if self.wave == None:
            return 0
        return self.wave.getNextValue()

    def getFrequency(self):
        if self.wave == None:
            return None
        else:
            return self.wave.getFrequency()

class MidiPlayer:

    def __init__(self, eventList, tuningSystem, samplingRate = 44100, maxValue = 10000):
	self.tuningSystem = tuningSystem
        self.tracks = []
        i = 0
        while i <= eventList.trackNumber: # TODO is there another way to do this?
            self.tracks.append(TrackPlayer(tuningSystem))
            i += 1
        self.eventList = eventList
        self.samplingRate = samplingRate
        self.maxValue = maxValue

    def getNote(self, midiEvent):
        """
        Return the note for a given midi event
        0 = C0
        """
        pitch = midiEvent.pitch
        index = pitch / 12 - 1
        alter = pitch % 12
        if alter == 0:
            return MusicalNote(MusicalNote.NOTE_C, 0, index)
        elif alter == 1:
           return MusicalNote(MusicalNote.NOTE_C, 1, index)
        elif alter == 2:
            return MusicalNote(MusicalNote.NOTE_D, 0, index)
        elif alter == 3:
            return MusicalNote(MusicalNote.NOTE_D, 1, index)
        elif alter == 4:
            return MusicalNote(MusicalNote.NOTE_E, 0, index)
        elif alter == 5:
            return MusicalNote(MusicalNote.NOTE_F, 0, index)
        elif alter == 6:
            return MusicalNote(MusicalNote.NOTE_F, 1, index)
        elif alter == 7:
            return MusicalNote(MusicalNote.NOTE_G, 0, index)
        elif alter == 8:
            return MusicalNote(MusicalNote.NOTE_G, 1, index)
        elif alter == 9:
            return MusicalNote(MusicalNote.NOTE_A, 0, index)
        elif alter == 10:
            return MusicalNote(MusicalNote.NOTE_B, -1, index)
        elif alter == 11:
            return MusicalNote(MusicalNote.NOTE_B, 0, index)

    def play(self):
        wavePlayer = WavePlayer()
        midiTicksPerSecond = 400 # don't know how to calculate this at the time

        currentNode = self.eventList.firstNode
        soundingTracks = 0 # Number of tracks that are sounding
        while currentNode != None and currentNode.nextNode != None:
            eventDuration = currentNode.getDuration()

            # what does each track play for this event?
            sys.stderr.write("Tick " + str(currentNode.time) + "\n")
            for event in currentNode.events:
                if event.type == "NOTE_ON":
                    # have to play something on a track
                    if event.velocity == 0:
                        # the note has to be muted
                        sys.stderr.write("\tMuting " + str(self.tracks[event.track.index].getFrequency()) + " Htz\n")
                        self.tracks[event.track.index].play(None)
                        soundingTracks-=1
                    else:
                        # this is the note to play on this track
                        self.tracks[event.track.index].play(self.getNote(event))
                        sys.stderr.write("\tStarting " + str(self.tracks[event.track.index].getFrequency()) + " Htz\n")
                        soundingTracks+=1

            # Let's play
            limit = int(currentNode.getDuration() * 44100 / midiTicksPerSecond)
            sampleCounter = 0
            while sampleCounter < limit:
                if soundingTracks == 0:
                    playValue = 0
                else:
                    accumulator = 0
                    for track in self.tracks:
                        accumulator += track.getNextValue()
                    playValue = int(accumulator / soundingTracks)
                
                wavePlayer.play(playValue)
                sampleCounter += 1

            currentNode = currentNode.nextNode
        sys.stdout.flush()        
        sys.stderr.write("Finished writing output\n")


def main(argv):
    argc = len(argv)
    if (argc == 1):
        sys.stderr.write("In order to play a file, you can provide the system you want to use to play it\n")
        sys.stderr.write("Pythagorean: specify a p and optionally the base frequency of A4\n")
        sys.stderr.write("\tEx: playmidi.py p 442 midi-file.mid\n")
        sys.stderr.write("Just system: specify a j and the key to use (only major keys, so if it's B minor set it to F).\n")
        sys.stderr.write("\tOptionally set the base freq of the base note of the key\n")
        sys.stderr.write("\tEx: playmidi.py j Bb midi-file.mid\n")
        sys.stderr.write("\tEx: playmidi.py j A 442 midi-file.mid\n")
        sys.stderr.write("If you want to use tempered system, don't specify anything. Optionally the freq of A4\n")
        sys.stderr.write("\tEx: playmidi.py 441 midi-file.mid\n")
        sys.stderr.flush()
        sys.exit(1)

    system = None
    fileName = None

    if argv[1] == "p":
        system = argv
        # pythagorean
        # was the frequency for A4 specified?
        baseFreq = 440
        try:
            baseFreq = int(argv[2])
            if argc >= 3:
                fileName = argv[3]
        except:
            # probably frequency wasn't provided
            fileName = argv[2]
        # Let's create the tuning system
        system = PythagoreanSystem(baseFreq)
    elif argv[1] == "j":
        # Just.... have to provide the key note
        keyNoteStr = argv[2].lower()
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
            keyNote = MusicalNote.NOTE_F
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
        fileName = argv[3]
    else:
        # Tempered System
        try:
            baseFreq = int(argv[1])
            system = TemperedSystem(baseFreq)
            fileName = argv[2]
        except:
            system = TemperedSystem.getInstance()
            fileName = argv[1]

    if fileName == None:
        sys.stderr.write("Didn't provide any file name to play\n")
        sys.stderr.flush()
        sys.exit(1)
    
    sys.stderr.write("reading file " + fileName + "\n")
    midiFile = MidiFile()
    midiFile.open(fileName)
    midiFile.read()
    midiFile.close()
    sys.stderr.write("File successfully read!\n")
    sys.stderr.write("There are " + str(len(midiFile.tracks)) + " tracks in the file\n")
    index = 0
    for track in midiFile.tracks:
        index += 1
        sys.stderr.write("Track " + str(index) + " has " + str(len(track.events)) + " events\n")

    sys.stderr.write("Let's process all the events\n")
    eventList = EventList()
    for track in midiFile.tracks:
        for event in track.events:
            eventList.addEvent(event)

    # let's reproduce the file
    sys.stderr.write("Starting to play file\n")
    midiPlayer = MidiPlayer(eventList, system)
    midiPlayer.play()
    sys.stderr.write("Finished playing\n")

if __name__ == "__main__":
    main(sys.argv)

#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright 2009 Edmundo Carmona Antoranz
Released under the terms of the Affero GPLv3
"""

from midi import *
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

    def printEvents(self):
        node = self.firstNode
        while node != None:
            sys.stderr.write("Time: " + str(node.time) + "\n")
            for event in node.events:
                sys.stderr.write("\t" + str(event) + "\n")
            node = node.nextNode

class MidiPlayer:

    def __init__(self, eventList, samplingRate = 44100, maxValue = 10000):
        self.tracks = []
        self.eventList = eventList
        self.samplingRate = samplingRate
        self.maxValue = maxValue

    def getNote(self, midiEvent):
        """
        Return the note for a given midi event
        0 = C0
        """
        pitch = midiEvent.pitch
        index = midiEvent % 12
        alter = pitch - index * 12
        if alter == 0:
            return MusicalNote(MusicalNote.NOTE_C, 0, index)
        elif alter == 1:
           return MusicalNote(MusicalNote.NOTE_C, 1, index)
        elif alter == 2:
            return MusicalNote(MusicalNote.NOTE_D, 0, index)
        elif alter == 3:
            return MusicalNote(MusicalNote.NOTE_D, 1, index)

    def play(self):
        midiTicksPerSecond = 400 # don't know how to calculate this at the time

        sampleCounter = 0
        currentNode = self.eventList.firstNode
        while currentNode != None:
            eventDuration = currentNode.getDuration()

            # what does each track play for this event?
            for event in currentNode.events:
                if event.type == "NOTE_ON":
                    track = event.track.index
                    sys.stderr.write("Track: " + str(track)+ "\n")
                    if event.velocity == 0:
                        self.tracks[track] = None
                    else:
                        self.tracks[track] = None # TODO Have to get the note from the pitch
            
            currentNode = currentNode.nextNode
        
        sys.stderr.write("Finished writing output\n")


def main(argv):
    inputfile = argv[1]
    sys.stderr.write("reading file " + inputfile + "\n")
    midiFile = MidiFile()
    midiFile.open(inputfile)
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
    midiPlayer = MidiPlayer(eventList)
    midiPlayer.play()
    sys.stderr.write("Finished playing\n")

if __name__ == "__main__":
    main(sys.argv)

#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright 2009 Edmundo Carmona
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
            print "Time: " + str(node.time)
            for event in node.events:
                print "\t" + str(event)
            node = node.nextNode

def main(argv):
    inputfile = argv[1]
    print "reading file " + inputfile
    midiFile = MidiFile()
    midiFile.open(inputfile)
    midiFile.read()
    midiFile.close()
    print "File successfully read!"
    print "There are " + str(len(midiFile.tracks)) + " tracks in the file"
    index = 0
    for track in midiFile.tracks:
        index += 1
        print "Track " + str(index) + " has " + str(len(track.events)) + " events"

    print "Let's process all the events"
    eventList = EventList()
    for track in midiFile.tracks:
        for event in track.events:
            eventList.addEvent(event)
    eventList.printEvents()

if __name__ == "__main__":
    main(sys.argv)

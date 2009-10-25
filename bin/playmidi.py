#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright 2009 Edmundo Carmona
Released under the terms of the Affero GPLv3
"""

from midi import *
import sys

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

if __name__ == "__main__":
    main(sys.argv)

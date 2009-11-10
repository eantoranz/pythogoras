#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2009 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

import sys
from Music import *

def main(argv):
    argc = len(argv)
    if (argc == 1):
        sys.stderr.write("Will display the frequencies between C4 and B4 with alterations\n")
        sys.stderr.write("Pythagorean: specify a p and optionally the base frequency of A4\n")
        sys.stderr.write("\tEx: ShowFrequencies.py p 442\n")
        sys.stderr.write("Just system: specify a j and the key note to use. For alterations use b or #.\n")
        sys.stderr.write("\tOptionally set the base freq of the base note of the key on index 4\n")
        sys.stderr.write("\tEx: ShowFrequencies.py j Bb\n")
        sys.stderr.write("\tEx: ShowFrequencies.py j A 442\n")
        sys.stderr.write("If you want to use tempered system specify a t. Optionally the freq of A4\n")
        sys.stderr.write("\tEx: ShowFrequencies.py t 441\n")
        sys.stderr.flush()
        sys.exit(1)

    system = None

    if argv[1] == "p":
        system = argv
        # pythagorean
        # was the frequency for A4 specified?
        baseFreq = 440
        if argc > 2:
            baseFreq = int(argv[2])
        else:
            # probably frequency wasn't provided
            baseFreq = 440

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
        # TODO Get the base frequency if provided by the user
        system = JustSystem(keyNote, alteration)
    elif argv[1] == 't':
        # Tempered System
        if argc > 2:
            baseFreq = int(argv[2])
            system = TemperedSystem(baseFreq)
        else:
            system = TemperedSystem.getInstance()

    for note in [ MusicalNote.NOTE_C, MusicalNote.NOTE_D, MusicalNote.NOTE_E, MusicalNote.NOTE_F, MusicalNote.NOTE_G, MusicalNote.NOTE_A, MusicalNote.NOTE_B ]:
        for alteration in [ -1, 0, 1 ]:
            newNote=MusicalNote(note, alteration, 4)
            sys.stdout.write(newNote.toString() + "\tFreq: " + str(system.getFrequency(newNote)) + "\n")


if __name__ == "__main__":
    main(sys.argv)

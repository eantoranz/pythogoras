#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2009 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

import sys
from WaveCommon import *

note1 = MusicalNote(MusicalNote.NOTE_A, 0, 4)
note2 = MusicalNote(MusicalNote.NOTE_A, 0, 4)
diff = note1.getDifference(note2)
if diff != [0, 0]:
    print "1st comparisson is broken " + str(diff)
    sys.exit(1)

note2 = MusicalNote(MusicalNote.NOTE_B, 0, 4)
diff = note1.getDifference(note2)
if diff != [1, 1]:
    print "2nd comparisson is broken " + str(diff)
    sys.exit(1)

diff = note2.getDifference(note1)
if diff != [-1, -1]:
    print "3rd comparisson is broken " + str(diff)
    sys.exit(1)

note2 = MusicalNote(MusicalNote.NOTE_B, -1, 4)
diff = note1.getDifference(note2)
if diff != [1, 0]:
    print "4th comparisson is broken " + str(diff)
    sys.exit(1)

note2 = MusicalNote(MusicalNote.NOTE_B, 1, 4)
diff = note1.getDifference(note2)
if diff != [1, 2]:
    print "5th comparisson is broken " + str(diff)
    sys.exit(1)

note2 = MusicalNote(MusicalNote.NOTE_C, 0, 5)
diff = note1.getDifference(note2)
if diff != [2, 1]:
    print "6th comparisson is broken " + str(diff)
    sys.exit(1)

print "All tests are OK"
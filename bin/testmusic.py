#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2009 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

import sys
from WaveCommon import *

note1 = MusicalNote(MusicalNote.NOTE_A, 0, 4)
note2 = MusicalNote(MusicalNote.NOTE_A, 0, 4)
diff = note1.getDistance(note2)
if diff != [0, 0]:
    print "1st comparisson is broken " + str(diff)
    sys.exit(1)

note2 = MusicalNote(MusicalNote.NOTE_B, 0, 4)
diff = note1.getDistance(note2)
if diff != [1, 1]:
    print "2nd comparisson is broken " + str(diff)
    sys.exit(1)

diff = note2.getDistance(note1)
if diff != [-1, -1]:
    print "3rd comparisson is broken " + str(diff)
    sys.exit(1)

note2 = MusicalNote(MusicalNote.NOTE_B, -1, 4)
diff = note1.getDistance(note2)
if diff != [1, 0]:
    print "4th comparisson is broken " + str(diff)
    sys.exit(1)

note2 = MusicalNote(MusicalNote.NOTE_B, 1, 4)
diff = note1.getDistance(note2)
if diff != [1, 2]:
    print "5th comparisson is broken " + str(diff)
    sys.exit(1)

note2 = MusicalNote(MusicalNote.NOTE_C, 0, 5)
diff = note1.getDistance(note2)
if diff != [2, 1]:
    print "6th comparisson is broken " + str(diff)
    sys.exit(1)

note1 = MusicalNote(MusicalNote.NOTE_D, 1, 6)
note2 = MusicalNote(MusicalNote.NOTE_G, -1, 4)
diff = note1.getDistance(note2)
if diff != [-11, -10]:
    print "7th comparisson is broken " + str(diff)
    sys.exit(1)

tempered = TemperedSystem.getInstance()
pythagorean = PythagoreanSystem.getInstance()
justC = JustSystem(MusicalNote.NOTE_C, 0)
justD = JustSystem(MusicalNote.NOTE_D, 0)
justA = JustSystem(MusicalNote.NOTE_A, 0)

note1 = MusicalNote(MusicalNote.NOTE_A, 0, 4)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_B, -1, 4)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_B, 0, 4)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_C, 0, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_C, 1, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_D, -1, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_D, 0, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_D, 1, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_E, -1, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_E, 0, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_E, 1, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_F, 0, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_F, 1, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_G, -1, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_G, 0, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_A, -2, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_A, -1, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))
note1 = MusicalNote(MusicalNote.NOTE_A, 0, 5)
print "Frequency of " + note1.toString() + " is "
print "\tTemp  : " + str(tempered.getFrequency(note1))
print "\tPyth  : " + str(pythagorean.getFrequency(note1))
print "\tJust C: " + str(justC.getFrequency(note1))
print "\tJust D: " + str(justD.getFrequency(note1))
print "\tJust A: " + str(justA.getFrequency(note1))

print "All tests are OK"
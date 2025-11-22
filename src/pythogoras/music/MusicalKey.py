# -*- coding: utf-8 -*-

# Copyright (c) 2009-2025 Edmundo Carmona Antoranz
# For licensing terms, check docs/LICENSING.txt

from pythogoras.music import MusicalNote


class MusicalKey:

    def __init__(self, note, alteration, major):
        self.note = note
        self.alteration = alteration
        self.major = major

    def toString(self):
        if self.note == MusicalNote.NOTE_A:
            note = "A"
        elif self.note == MusicalNote.NOTE_B:
            note = "B"
        elif self.note == MusicalNote.NOTE_C:
            note = "C"
        elif self.note == MusicalNote.NOTE_D:
            note = "D"
        elif self.note == MusicalNote.NOTE_E:
            note = "E"
        elif self.note == MusicalNote.NOTE_F:
            note = "F"
        elif self.note == MusicalNote.NOTE_G:
            note = "G"
        else:
            raise Exception("Unknown note in musical key: " + str(self.note))

        if self.alteration < 0:
            alteration = (self.alteration * -1) * "b"
        elif self.alteration > 0:
            alteration = self.alteration * "#"
        else:
            alteration = ""

        if self.major:
            major = "Major"
        else:
            major = "Minor"

        return "Key: " + note + alteration + " " + major

    def __str__(self):
        return self.toString()

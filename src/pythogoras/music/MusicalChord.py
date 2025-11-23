# -*- coding: utf-8 -*-

# Copyright (c) 2009-2025 Edmundo Carmona Antoranz
# For licensing terms, check docs/LICENSING.txt


class MusicalChord:

    def __init__(self, notes, duration):
        self.notes = notes
        for note in notes:
            note.setDuration(duration, True)

    def toString(self):
        temp = "Chord. Duration: " + str(self.notes[0].duration)
        if self.notes[0].dots:
            temp += "."
        temp += " Notes: "

        firstNote = True
        for note in self.notes:
            if firstNote:
                firstNote = False
            else:
                temp += " "
            temp += note.toString(False)
        return temp

    def __str__(self):
        return self.toString()

    def getDuration(self):
        return self.notes[0].duration

    def getDots(self):
        return self.notes[0].dots

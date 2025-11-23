# -*- coding: utf-8 -*-

# Copyright 2009-2025 Edmundo Carmona Antoranz
# For licensing terms, check docs/LICENSING.txt

from pythogoras.music.MusicalNote import MusicalNote


class TuningSystem:

    FREQ_A4 = 440
    A4 = MusicalNote(MusicalNote.NOTE_A, 0, 4)

    def getFrequency(self, note):
        return 0

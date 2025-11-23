# -*- coding: utf-8 -*-

# Copyright (c) 2009-2025 Edmundo Carmona Antoranz
# For licensing terms, check docs/LICENSING.txt


class MusicalPolyphony:

    def __init__(self, voices):
        self.voices = voices

    def toString(self):
        temp = "Polyphony\n"
        counter = 1
        for voice in self.voices:
            temp += "Voice " + str(counter) + ":"
            for element in voice:
                temp += " " + str(element)
            temp += "\n"
            counter += 1

        return temp

    def __str__(self):
        return self.toString()

    def getVoices(self):
        return self.voices

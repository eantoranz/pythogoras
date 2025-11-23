#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright (c) 2009-2025 Edmundo Carmona Antoranz
For licensing terms, check docs/LICENSING.txt
"""

import argparse
import lilypy
import math
import sys

from pythogoras.music.MusicalChord import MusicalChord
from pythogoras.music.MusicalKey import MusicalKey
from pythogoras.music.MusicalNote import MusicalNote
from pythogoras.music.MusicalPolyphony import MusicalPolyphony
from pythogoras.music.tuning.JustSystem import JustSystem
from pythogoras.music.tuning.PythagoreanSystem import PythagoreanSystem
from pythogoras.music.tuning.TemperedSystem import TemperedSystem
from pythogoras.music.tuning.TuningSystem import TuningSystem
from Wave import Wave
from WavePlayer import WavePlayer


class LilypondNotePlayer:

    def __init__(
        self, beatsPerMinute, beatUnit, tuningSystem, note, samplingRate=44100
    ):
        self.note = note
        self.volume = 1  # Full colume for starters
        self.samplingRate = samplingRate
        # How many samples will I have to play?
        self.totalSamples = int(
            beatUnit * samplingRate * 60 / (note.duration * beatsPerMinute)
        )
        if self.note.times != None:
            self.totalSamples /= self.note.times
        if note.dots:
            self.totalSamples = int(self.totalSamples * (2.0 - pow(2, -note.dots)))
        self.wave = Wave(tuningSystem.getFrequency(note), samplingRate)
        self.counter = 0
        self.volumeRate = None
        self.tied = False

    def getNextValue(self):
        self.counter += 1

        # Do we have to lower the volume?
        if (
            not self.tied
            and self.totalSamples - self.counter <= self.samplingRate * 0.05
        ):  # 5 hundredths of a second
            # Have to calculate a volume rate
            if self.totalSamples <= self.counter:
                self.volumeRate = 0
            else:
                self.volumeRate = math.exp(
                    math.log(0.01) / (self.totalSamples - self.counter)
                )
            sys.stderr.flush()
        if self.volumeRate != None:
            self.wave.setVolume(self.volume * self.volumeRate)

        return self.wave.getNextValue()

    def setTied(self, value):
        self.tied = value

    def isTied(self):
        return self.tied

    def isFinished(self):
        return self.counter >= self.totalSamples

    def setNewDuration(self, totalSamples):
        self.counter = 0
        self.totalSamples = totalSamples

    def getAngle(self):
        return self.wave.getAngle()

    def setAngle(self, angle):
        self.wave.setAngle(angle)

    def getFrequency(self):
        return self.wave.getFrequency()


class LilypondChordPlayer:

    def __init__(
        self, beatsPerMinute, beatUnit, tuningSystem, chord, samplingRate=44100
    ):
        """
        A chord player
        """
        # Create a number of note players and that's it
        self.players = []
        for note in chord.notes:
            self.players.append(
                LilypondNotePlayer(
                    beatsPerMinute, beatUnit, tuningSystem, note, samplingRate
                )
            )
        self.length = len(self.players)

    def getNextValue(self):
        accumulator = 0
        for player in self.players:
            accumulator += player.getNextValue()
        return int(accumulator / self.length)

    def isFinished(self):
        return self.players[0].isFinished()

    def setAngle(self, angle):
        # will place the first player to the desired position so that it takes over the wave that was left before
        # the other players will start from 0
        self.players[0].setAngle(angle)

    def getAngle(self):
        tangents = list()
        for player in self.players:
            tangents.append(math.tan(player.getAngle()))
        # now we calculate the final angle
        sumatory = 0
        multiples = 1
        for tangent in tangents:
            sumatory += tangent
            multiples += tangent
        if multiples == 1:
            # would return 0
            return 0
        else:
            return math.atan(sumatory / (1 - multiples))


class LilypondPolyphonyPlayer:

    def __init__(
        self, beatsPerMinute, beatUnit, tuningSystem, polyphony, samplingRate=44100
    ):
        # perhaps the simplest solution is to use staff players for each voice
        self.players = list()
        self.voices = len(polyphony.voices)  # number of voices
        for voice in polyphony.voices:
            staff = lilypy.LilypondStaff()
            staff.events = voice
            player = LilypondStaffPlayer(
                beatsPerMinute, tuningSystem, staff, samplingRate
            )
            player.beatUnit = beatUnit
            self.players.append(player)

    def getNextValue(self):
        temp = 0
        for player in self.players:
            temp += player.getNextValue()
            if player.isFinished():
                self.players.remove(player)
        return temp / self.voices

    def isFinished(self):
        # will return True if all players are finished
        return len(self.players) == 0

    def getAngle(self):
        return 0

    def setAngle(self, angle):
        None


class LilypondStaffPlayer:

    def __init__(self, beatsPerMinute, tuningSystem, staff, samplingRate=44100):
        """
        A Staff Player
        """
        self.beatsPerMinute = beatsPerMinute
        self.staff = staff
        # beat unit from Time Marker
        self.beatUnit = self.staff.getFirstTimeMarker().denominator
        self.tuningSystem = tuningSystem
        self.samplingRate = samplingRate

        self.eventPlayer = None  # Nothing is being played right now
        self.eventCounterIndex = -1

        self.finished = False

    def getNextValue(self):
        if self.eventPlayer == None:
            # What's the next event?
            while True:
                self.eventCounterIndex += 1
                if self.eventCounterIndex < len(self.staff.events):
                    self.event = self.staff.events[self.eventCounterIndex]
                    if isinstance(self.event, MusicalNote):
                        self.eventPlayer = LilypondNotePlayer(
                            self.beatsPerMinute,
                            self.beatUnit,
                            self.tuningSystem,
                            self.event,
                            self.samplingRate,
                        )
                        # considering ties
                        if self.eventCounterIndex + 1 < len(
                            self.staff.events
                        ) and isinstance(
                            self.staff.events[self.eventCounterIndex + 1],
                            lilypy.LilypondTie,
                        ):
                            # note has to be tied to the next
                            self.eventPlayer.setTied(True)
                        break
                    elif isinstance(self.event, MusicalChord):
                        self.eventPlayer = LilypondChordPlayer(
                            self.beatsPerMinute,
                            self.beatUnit,
                            self.tuningSystem,
                            self.event,
                            self.samplingRate,
                        )
                        break
                    elif isinstance(self.event, MusicalPolyphony):
                        self.eventPlayer = LilypondPolyphonyPlayer(
                            self.beatsPerMinute,
                            self.beatUnit,
                            self.tuningSystem,
                            self.event,
                            self.samplingRate,
                        )
                        break
                    elif isinstance(self.event, lilypy.LilypondTie):
                        sys.stderr.flush()
                        self.eventCounterIndex += (
                            1  # let's use a new player and set the angle accordingly
                        )
                        self.event = self.staff.events[self.eventCounterIndex]
                        if isinstance(self.event, MusicalNote):
                            self.eventPlayer = LilypondNotePlayer(
                                self.beatsPerMinute,
                                self.beatUnit,
                                self.tuningSystem,
                                self.event,
                                self.samplingRate,
                            )
                            self.eventPlayer.setAngle(self.lastAngle)
                            self.eventPlayer.setTied(False)
                        else:
                            # it's a chord
                            self.eventPlayer = LilypondChordPlayer(
                                self.beatsPerMinute,
                                self.beatUnit,
                                self.tuningSystem,
                                self.event,
                                self.samplingRate,
                            )
                            self.eventPlayer.setAngle(self.lastAngle)
                        break
                    elif isinstance(self.event, MusicalKey):
                        # If it's just system, have to change it
                        if isinstance(self.tuningSystem, JustSystem):
                            # Frequency of the new base note under the actual tuning system
                            newBaseNote = MusicalNote(
                                self.event.note, self.event.alteration, 4
                            )
                            newBaseFreq = self.tuningSystem.getFrequency(newBaseNote)
                            sys.stderr.write(
                                "Modulating to "
                                + newBaseNote.toString()
                                + " set to "
                                + str(newBaseFreq)
                                + "\n"
                            )
                            self.tuningSystem = JustSystem(
                                self.event.note, self.event.alteration, newBaseFreq
                            )
                    elif isinstance(self.event, lilypy.LilypondTie):
                        # it should have already been processed
                        None
                    else:
                        sys.stderr.write(
                            "Unknown event " + self.event.toString() + "\n"
                        )
                else:
                    break
            if self.eventCounterIndex >= len(self.staff.events):
                # Finished
                self.finished = True
                return 0
        temp = self.eventPlayer.getNextValue()
        if self.eventPlayer.isFinished():
            self.lastAngle = self.eventPlayer.getAngle()
            self.eventPlayer = None  # Have to get the next event
        return temp

    def isFinished(self):
        return self.finished


class LilypondSystemPlayer:
    """
    Class that can play a system instead of just a staff
    """

    def __init__(self, beatsPerMinute, tuningSystem, system, samplingRate=44100):
        self.players = []
        for staff in system.staffs:
            self.players.append(
                LilypondStaffPlayer(beatsPerMinute, tuningSystem, staff, samplingRate)
            )
        self.length = len(self.players)

    def getNextValue(self):
        accumulator = 0
        for player in self.players:
            if player.finished:
                self.players.remove(player)
                self.length -= 1
                continue
            accumulator += player.getNextValue()
        if self.length == 0:
            return 0
        return int(accumulator / self.length)

    def isFinished(self):
        return self.length <= 0


class LilypondPlayer:
    """
    Class that can play from a staff or a system
    """

    SYSTEM_EQUAL_TEMPERED = 1
    SYSTEM_PYTHAGOREAN = 2
    SYSTEM_JUST = 3

    def __init__(self, beatsPerMinute, tuningSystem, baseFreq, wavePlayer):
        self.beatsPerMinute = beatsPerMinute
        self.wavePlayer = wavePlayer
        self.tuningSystem = tuningSystem
        self.baseFreq = baseFreq
        self.samplingRate = wavePlayer.samplingRate

    def playSystem(self, system):
        """
        play from a lilypond system
        """
        player = None
        if self.tuningSystem == LilypondPlayer.SYSTEM_EQUAL_TEMPERED:
            if self.baseFreq == None:
                self.baseFreq = TuningSystem.FREQ_A4
            player = LilypondSystemPlayer(
                self.beatsPerMinute,
                TemperedSystem(self.baseFreq),
                system,
                self.samplingRate,
            )
        elif self.tuningSystem == LilypondPlayer.SYSTEM_PYTHAGOREAN:
            if self.baseFreq == None:
                self.baseFreq = TuningSystem.FREQ_A4
            player = LilypondSystemPlayer(
                self.beatsPerMinute,
                PythagoreanSystem(self.baseFreq),
                system,
                self.samplingRate,
            )
        elif self.tuningSystem == LilypondPlayer.SYSTEM_JUST:
            key = system.staffs[0].getFirstKey()
            player = LilypondSystemPlayer(
                self.beatsPerMinute,
                JustSystem(key.note, key.alteration, self.baseFreq),
                system,
                self.samplingRate,
            )
        else:
            sys.stderr.write(
                "Don't know what tuning system to use to play lilypond file\n"
            )
            sys.stderr.flush()
            sys.exit(1)

        while not player.isFinished():
            self.wavePlayer.play(player.getNextValue())
        sys.stderr.write("Finished playing system\n")
        sys.stderr.flush()
        # finished playing

    def playStaff(self, staff):
        """
        Play from a staff
        """
        player = None
        if self.tuningSystem == LilypondPlayer.SYSTEM_EQUAL_TEMPERED:
            if self.baseFreq == None:
                self.baseFreq = TuningSystem.FREQ_A4
            player = LilypondStaffPlayer(
                self.beatsPerMinute,
                TemperedSystem(self.baseFreq),
                staff,
                self.samplingRate,
            )
        elif self.tuningSystem == LilypondPlayer.SYSTEM_PYTHAGOREAN:
            if self.baseFreq == None:
                self.baseFreq = TuningSystem.FREQ_A4
            player = LilypondStaffPlayer(
                self.beatsPerMinute,
                PythagoreanSystem(self.baseFreq),
                staff,
                self.samplingRate,
            )
        elif self.tuningSystem == LilypondPlayer.SYSTEM_JUST:
            key = staff.getFirstKey()
            player = LilypondStaffPlayer(
                self.beatsPerMinute,
                JustSystem(key.note, key.alteration, self.baseFreq),
                staff,
                self.samplingRate,
            )
        else:
            sys.stderr.write(
                "Don't know what tuning system to use to play lilypond file\n"
            )
            sys.stderr.flush()
            sys.exit(1)
        while not player.finished:
            self.wavePlayer.play(player.getNextValue())
        sys.stderr.write("Finished playing\n")
        sys.stderr.flush()
        # Finished playing


def main(argv):

    parser = argparse.ArgumentParser(description="Synthesyze lilypond files")
    parser.add_argument("file", type=argparse.FileType("r"), nargs=1)
    parser.add_argument(
        "-b",
        "--beats-per-minute",
        action="store",
        default=60,
        type=float,
        help="Beats per minute",
        metavar="BPM",
        dest="speed",
    )
    parser.add_argument(
        "-s",
        "--system",
        action="store",
        default="tempered",
        choices=["pyth", "just", "equal"],
        help="Intonation system",
        dest="system",
    )
    parser.add_argument(
        "-bf",
        "--base-frequency",
        action="store",
        type=float,
        help="Frequency of key note (index 4)",
        dest="baseFreq",
    )
    parser.add_argument(
        "-sr",
        "--sampling-rate",
        type=int,
        help="Sampling rate Frequency (Htz). Default: 44100.",
        default=44100,
    )
    parser.add_argument(
        "-out",
        action="store",
        choices=["alsa", "-"],
        help="Output to use to synthesize. Default: alsa",
        default="alsa",
        dest="output",
    )

    args = parser.parse_args(argv[1:])

    speed = args.speed
    system = args.system
    baseFreq = args.baseFreq
    inputFile = args.file
    outputFile = args.output

    if system == "pyth":
        # pythagorean
        # Let's create the tuning system
        system = LilypondPlayer.SYSTEM_PYTHAGOREAN
        # was the frequency for A4 specified?
    elif system == "just":
        # Just.... have to provide the key note
        system = LilypondPlayer.SYSTEM_JUST
        # TODO how about the key note?
    else:
        # Tempered System
        system = LilypondPlayer.SYSTEM_EQUAL_TEMPERED

    if outputFile != "alsa":
        outputFile = sys.stdout
    else:
        outputFile = None  # alsa

    sys.stderr.write("reading file\n")

    # Create a lilypond analyser
    analyser = lilypy.LilypondAnalyser()
    analyser.analyseFile(inputFile[0])
    sys.stderr.write("Finished analyzing file\n")

    lilyPlayer = LilypondPlayer(
        speed, system, baseFreq, WavePlayer(args.sampling_rate, outputFile)
    )
    systems = analyser.systems
    if len(systems) > 0:
        # Have to play the systems
        for system in systems:
            lilyPlayer.playSystem(system)
        sys.exit(0)
    # No systems.... let's check staffs
    staffs = analyser.staffs
    if len(staffs) > 0:
        for staff in staffs:
            lilyPlayer.playStaff(staff)
        sys.exit(0)
    sys.stderr.write("No lilypond systems or staffs to play")
    sys.exit(-1)


if __name__ == "__main__":
    main(sys.argv)

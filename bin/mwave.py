#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2009 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

import Wave

wave = Wave.Wave(1)
i = 0
while i < 44100:
    print(wave.getNextValue())
    i+=1
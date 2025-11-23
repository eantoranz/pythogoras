#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2009-2025 Edmundo Carmona Antoranz
# Released under the terms of the Affero GPLv3

import Wave

wave = Wave.Wave(.3)
i = 0
while i < 44100:
    print(wave.getNextValue())
    i+=1
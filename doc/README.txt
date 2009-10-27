Eventually, this will reproduce midi files. I'm still not very close to that, though

If you use SoundPlayer.py from the console, you could hear something by piping to asound like this:
./SoundPlayer.py | aplay -f U16_BE -r 44100 -c 2


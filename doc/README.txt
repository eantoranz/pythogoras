Edmundo Carmona Antoranz eantoranz gmail com

Eventually, this will reproduce midi files. I'm still not very close to that, though

WavePlayer:
    With this application you can reproduce sine waves. You can provide a single frequency for both channels
    or a frequency for the left channel and another for the right one.

    Usage:
        Provide either a single frequency for both channels or two frequencies being the left channel the first argument.

        Examples
            Reproduce a single A4 on both channels:
                ./WavePlayer.py 440
            Reproduce an A4 on the left channel and a E5 (pythagorean) on the right channel:
                ./WavePlayer.py 440 660
            It can be used to reproduce inverted waves (starting by a valley instead of a peak) by using a negative frequency:
                ./WavePlayer.py -440
            What happens if you play a positive wave against a negative one facing one speaker to the other? That
            should be interesting:
                ./WavePlayer.py 440 -440

    Reproduction:
        If you use WavePlayer.py from the console, you could hear something by piping to asound like this:
        ./WavePlayer.py blah | aplay -f U16_BE -r 44100 -c 2


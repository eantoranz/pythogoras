The objective of this project would be to reproduce music using different tuning systems for reasearch.

Right now the project is able to reproduce a midi file included in the mid directory
Can also play simple lilypond files.
The output can be sent to standard output (to be saved as a file or pipe it into an encoder like oggenc or so) or can be
directly heard through alsa (that would be on GNU/Linux, in other operating systems, the direct sound programming would
have to be developed).

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

lilyplay.py:
    With this application, you could play (simple) lilypond files.
    
    run ./lyliplay.py -h
    
    Sampling
    lilyplay supports two types of sampling modes and they are set on a lilypond staff
    - Raw mode
      This mode reads a raw signed 16-bit 44.1 khtz as the sample for the instrument
      The file will be located in the directory of the samples (use option --sample-dir), the
      name you provide and the extension .raw as the file name
    - SHARC mode
      In this mode, the instrument definition is read from the SHARC db (set in on /usr/share/sharc).
      SHARC DB can be retrieved from here: http://www.timbre.ws/sharc/files/sharc.tar.gz
      SHARC DB is published by Greg Sandell
    
    In order to use sampling, add a comment like this to a staff
    For a raw sample:
      % \sample raw violin
    For a shark instrument sample:
      % \sample sharc violin_muted_vibrato
      

playmidi.py:
    With this application you could play midi files.

    Usage:
        In order to play a file, you can provide the system you want to use to play it
        Pythagorean: specify a p and optionally the base frequency of A4
            Ex: ./playmidi.py p 442 midi-file.mid
        Just system: specify a j and the key to use (only major keys, so if it's B minor set it to F).
            Optionally set the base freq of the base note of the key
            Ex: ./playmidi.py j Bb midi-file.mid
            Ex: ./playmidi.py j A 442 midi-file.mid
        If you want to use tempered system, don't specify anything. Optionally the freq of A4
            Ex: ./playmidi.py 441 midi-file.mid

Edmundo Carmona Antoranz <eantoranz at gmail dot com>
Bogota, Colombia


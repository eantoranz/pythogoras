class Sampler:
    """
        This wave can read from a sampling file and reproduce the wave as in the sampling file with the desired frequency
        
        The sampling file has to contain (at least for the moment) a single wave cycle. It can be any length and the sampling
        size will be used to calculate the original wave frequency
        
        Format of the sampling file:
        RAW PCM signed 16 bit mono, 44.1 khtz, little endian
    """
    
    sampleFreq = None # Frequency of the sample
    samples = []
    x0index = None # position of the first root (x where y = 0)
    x1index = None

    def __init__(self, samplingFile):
        # let's read the sampling file
        inputFile = open(samplingFile, 'r')
        # now we start reading numbers
        while (True):
            value = inputFile.read(2)
            if (len(value) < 2):
                # sample was incomplete.... we go out
                break
            # now we create the numeric sample
            sample = ord(value[1]) << 8 | ord(value[0]);
            if (sample & 0x8000 != 0):
                sample -= 0x10000
            self.samples.append(sample)
         
        # now we remove the extremes
        # first, at the begining
        while (self.samples[1] < 0):
            self.samples.pop(0)
        # then at the end
        while (self.samples[len(self.samples) - 2] > 0):
	    self.samples.pop()
        
        self.sampleFreq = 44100.0 / len(self.samples)
        self.x0index = float(self.samples[0]) / float(self.samples[0] - self.samples[1])
        self.x1index = len(self.samples) - 1 + float(self.samples[len(self.samples) - 2]) / float(self.samples[len(self.samples) - 2] - self.samples[len(self.samples) - 1])
    

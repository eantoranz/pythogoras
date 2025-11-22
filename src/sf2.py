#!/usr/bin/python

# copyright 2011 Edmundo Carmona Antoranz
# This file is released under the terms f Affero GPLv3

import sys
from StringIO import StringIO
from chunk import Chunk

def strToDWord(string):
    return ord(string[3])<<24 | ord(string[2])<<16 | ord(string[1])<<8 | ord(string[0])

def strToWord(string):
    return ord(string[1])<<8 | ord(string[0])

class SF2Parser:
    # this class is used to parse SF2 file contents
    
    SAMPLE_RECORDS = "shdr"
    SAMPLE = "smpl"
    INSTRUMENTS = "inst"
    INSTRUMENT_ZONES = "ibag"
    
    @classmethod
    def parseFromFile(cls, iFile, nodeName = None):
        # parse a file generating an SF2 tree structure
        
        # read stuff from file at the current position
        aChunk = Chunk(iFile, align=True, bigendian=False)
        ckID = aChunk.getname()
        ckSize = aChunk.getsize()
        ckData = aChunk.read()
        aChunk.close()
        
        # let's create a node from this data
        node = SF2Parser.createNode(nodeName, ckID, ckSize, ckData)
        
        # depending on the type of node, children could be inside of it
        SF2Parser.parseNode(node)
        
        # return the root node
        return node
    
    @classmethod
    def parseNode(cls, node):
        # depending on the type of node, other children could be inside of it...
        # if that's the case, create the children accordingly
        ckID = node.ckID
        if ckID in ["RIFF", "LIST"]:
            # There are children inside of it
            chunkName = node.ckData[0:4]
            data = StringIO(node.ckData[4:])
            # let's parse the data until it's empty
            try:
                while True:
                    # let's go on until we reach the end of file
                    child = SF2Parser.parseFromFile(data, chunkName)
                    node.addChild(child)
            except EOFError:
                #sys.stderr.write("Reached EOF... coming back a level\n")
                None
    
    @classmethod
    def createNode(cls, nodeName, ckID, ckSize, ckData):
        if ckID == SF2Parser.SAMPLE_RECORDS:
            # sample pointers
            return SF2ShdrNode(nodeName, ckID, ckSize, ckData)
        elif ckID == SF2Parser.INSTRUMENTS:
            return SF2InstNode(nodeName, ckID, ckSize, ckData)
        elif ckID == SF2Parser.INSTRUMENT_ZONES:
            return SF2InstrumentZoneNode(nodeName, ckID, ckSize, ckData)
        else:
            return SF2Node(nodeName, ckID, ckSize, ckData)
                

class SF2Node:
    # an SF2 node
    
    def __init__(self, name, ckID, ckSize, ckData, parent = None):
        (self.name, self.ckID, self.ckSize, self.ckData, self.parent) = (name, ckID, ckSize, ckData, parent)
        self.children = list()
    
    def addChild(self, child):
        # add another child to the SF2 node
        self.children.append(child)
    
    def getChild(self, childID, recursive = False):
        # return a child by its ckID
        for child in self.children:
            if child.ckID == childID:
                return child
        # it's not in this node directly
        if recursive:
            # let's try to find the child with this ckID in the children of this node
            for child in self.children:
                foundChild = child.getChild(childID, True)
                if foundChild != None:
                    # found the right child
                    return foundChild
    
    def getSample(self, shdrRecord):
        # get a sample given the shdrRecord
        # shrdRdcord can do it already
        return shdrRecord.getSample(self)
    
    def __str__(self):
        if self.name == None:
            name = "<None>"
        else:
            name = self.name
        return "Node " + name + ". ID: " + self.ckID + ". Size " + str(self.ckSize)

class SF2ShdrRecord:
    # one sample record information in shdr
    
    SAMPLE_TYPE_MONO = 1
    SAMPLE_TYPE_RIGHT = 2
    SAMPLE_TYPE_LEFT = 4
    SAMPLE_TYPE_LINKED = 8
    SAMPLE_TYPE_ROM_MONO = 8000 | SAMPLE_TYPE_MONO
    SAMPLE_TYPE_ROM_RIGHT = 8000 | SAMPLE_TYPE_RIGHT
    SAMPLE_TYPE_ROM_LEFT = 8000 | SAMPLE_TYPE_LEFT
    SAMPLE_TYPE_ROM_LINKED = 8000 | SAMPLE_TYPE_LINKED

    def __init__(self, name, start, end, loopStart, loopEnd, sampleRate, midiPitch, pitchCorrection, sampleLink, sampleType):
        (self.name, self.start, self.end, self.loopStart, self.loopEnd, self.sampleRate, self.midiPitch, self.pitchCorrection, self.sampleLink, self.sampleType) = (name, start, end, loopStart, loopEnd, sampleRate, midiPitch, pitchCorrection, sampleLink, sampleType)
    
    def __str__(self):
        # about sample type
        if self.sampleType == SF2ShdrRecord.SAMPLE_TYPE_MONO:
            sampleType = "Mono Sample"
        elif self.sampleType == SF2ShdrRecord.SAMPLE_TYPE_RIGHT:
            sampleType = "Right Sample"
        elif self.sampleType == SF2ShdrRecord.SAMPLE_TYPE_LEFT:
            sampleType = "Left Sample"
        elif self.sampleType == SF2ShdrRecord.SAMPLE_TYPE_LINKED:
            sampleType = "Linked Sample"
        elif self.sampleType == SF2ShdrRecord.SAMPLE_TYPE_ROM_MONO:
            sampleType = "ROM Mono Sample"
        elif self.sampleType == SF2ShdrRecord.SAMPLE_TYPE_ROM_RIGHT:
            sampleType = "ROM Right Sample"
        elif self.sampleType == SF2ShdrRecord.SAMPLE_TYPE_ROM_LEFT:
            sampleType = "ROM Left Sample"
        elif self.sampleType == SF2ShdrRecord.SAMPLE_TYPE_ROM_LINKED:
            sampleType = "ROM Linked Sample"
        else:
            # unknown TODO is it valid?
            sampleType = "Unknown (" + str(self.sampleType) + ")"
        
        return "Sample name: <" + self.name + ">. Start: " + str(self.start) + " End: " + str(self.end) + " Loop Start: " + str(self.loopStart) + " Loop End: " + str(self.loopEnd) + " Sample Rate: " + str(self.sampleRate) + " Midi Pitch: " + str(self.midiPitch) + " Pitch Correction: " + str(self.pitchCorrection) + " Sample Link: " + str(self.sampleLink) + " Sample Type: " + sampleType
    
    def getSample(self, tree):
        # get the sample from the appropiate node in the tree for this SHDR record
        if tree.ckID == SF2Parser.SAMPLE:
            # should find a child
            sampleNode = tree.getChild(SF2Parser.SAMPLE, True)
        else:
            sampleNode = tree
        
        # now let's get the information from the sample
        return tree.ckData[self.start:self.end + 1]

class SF2ShdrNode(SF2Node):
    # sample pointers
    
    def __init__(self, name, ckID, ckSize, ckData, parent = None):
        SF2Node.__init__(self, name, ckID, ckSize, ckData, parent = None)
        
        self.records = list()
        
        # let's break the information of the pointers
        # how many records are there?
        records = self.ckSize / 46 - 1 # last record is supposed to be empty
        for i in range(records):
            baseIndex = i * 46
            name = self.ckData[baseIndex:baseIndex + 20]
            start = strToDWord(self.ckData[baseIndex+20:baseIndex+24])
            end = strToDWord(self.ckData[baseIndex+24:baseIndex+28])
            loopStart = strToDWord(self.ckData[baseIndex+28:baseIndex+32])
            loopEnd = strToDWord(self.ckData[baseIndex+32:baseIndex+36])
            sampleRate = strToDWord(self.ckData[baseIndex+36:baseIndex+40])
            midiPitch = ord(self.ckData[baseIndex+40])
            pitchCorrection = ord(self.ckData[baseIndex+41]) # in cents
            sampleLink = strToWord(self.ckData[baseIndex+42:baseIndex+44])
            sampleType = strToWord(self.ckData[baseIndex+44:baseIndex+46])
            
            self.records.append(SF2ShdrRecord(name, start, end, loopStart, loopEnd, sampleRate, midiPitch, pitchCorrection, sampleLink, sampleType))
            
class SF2Instrument:
    # instrument in an SF2 file (defined in the INST block)

    def __init__(self, name, bagIndex):
        (self.name, self.bagIndex) = (name, bagIndex)
    
    def __str__(self):
        return "Intrument " + self.name + ". Bag Index: " + str(self.bagIndex)

class SF2InstNode(SF2Node):
    # instruments in the SF2 file
    
    def __init__(self, name, ckID, ckData, parent = None):
        SF2Node.__init__(self, name, ckID, ckData, parent)
        
        self.instruments = list()

        # now we have to process the instruments
        records = len(self.ckData) / 22
        for i in range(records):
            baseIndex = i * 22
            
            # data for the instrument record
            name = self.ckData[baseIndex:baseIndex+20]
            bagIndex = strToWord(self.ckData[baseIndex+20:baseIndex+22])
            
            self.instruments.append(SF2Instrument(name, bagIndex))

class SF2InstrumentZone:
    # an instrument zone... as found in the IBAG node
    # generatorsListIndex is the index of the instrument zone's list of generators in the IGEN node
    # modulatorsListIndex is the index of the instrument zone's list of modulatros in the IMOD node
    
    def __init__(self, generatorsListIndex, modulatorsListIndex):
        (self.generatorsListIndex, self.modulatorsListIndex) = (generatorsListIndex, modulatorsListIndex)

class SF2InstrumentZoneNode(SF2Node):
    # node with the instrument zones in the SF2 file (IBAG)
    
    def __init__(self, name, ckID, ckData, parent = None):
        SF2Node.__init__(self, name, ckID, ckData, parent)
        
        self.zones = list()
        
        records = len(self.ckData) / 4
        for i in range(records - 1):
            baseIndex = i * 4
            
            generatorsListIndex = strToWord(self.ckData[baseIndex:baseIndex+2])
            modulatorsListIndex = strToWord(self.ckData[baseIndex+2:baseIndex+4])
            
            self.zones.append(SF2InstrumentZone(generatorsListIndex, modulatorsListIndex))
            sys.stderr.write("Created instrument zone with generators list index of " + str(generatorsListIndex) + " and modulators list index of " + str(modulatorsListIndex) + "\n")


if __name__ == "__main__":
    # a file name should have been provided to be processed
    
    iFile = open(sys.argv[1], 'ro')
    sf2Tree = SF2Parser.parseFromFile(iFile)
    # let's print(some information about the SF2 file
    # engineer
    smpl = sf2Tree.getChild("smpl", True)
    sys.stdout.write(smpl.ckData)
    
    shdr = sf2Tree.getChild("shdr", True)
    sys.stderr.write("There are " + str(shdr.ckSize / 46) + " samples\n")
    
    for record in shdr.records:
        sys.stderr.write("SHDR record : " + str(record) + "\n")
        # let's try to get sample
        sample = record.getSample(sf2Tree)
        sys.stderr.write("Sample's size is " + str(len(sample)) + " and it was supposed to be " + str(record.end - record.start + 1) + "\n")
    
    #instruments
    sys.stderr.write("Instruments:\n")
    instruments = sf2Tree.getChild(SF2Parser.INSTRUMENTS, True)
    for instrument in instruments.instruments:
        sys.stderr.write("\t" + str(instrument) + "\n")
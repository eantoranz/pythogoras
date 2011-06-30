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
            # let's parse the data until it's empty all children are processed
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
        if ckID == "shdr":
            # sample pointers
            return SF2ShdrNode(nodeName, ckID, ckSize, ckData)
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
    
    def __str__(self):
        if self.name == None:
            name = "<None>"
        else:
            name = self.name
        return "Node " + name + ". ID: " + self.ckID + ". Size " + str(self.ckSize)

class SF2ShdrRecord:
    # one sample record information in shdr

    def __init__(self, name, start, end, loopStart, loopEnd, sampleRate, midiPitch, pitchCorrection, sampleLink, sampleType):
        (self.name, self.start, self.end, self.loopStart, self.loopEnd, self.sampleRate, self.midiPitch, self.pitchCorrection, self.sampleLink, self.sampleType) = (name, start, end, loopStart, loopEnd, sampleRate, midiPitch, pitchCorrection, sampleLink, sampleType)
    
    def __str__(self):
        # about sample type
        sampleType = self.sampleType & 0x7fff
        if sampleType == 1:
            sampleType = "Mono Sample"
        elif sampleType == 2:
            sampleType = "Right Sample"
        elif sampleType == 4:
            sampleType = "Left Sample"
        elif sampleType == 8:
            sampleType = "Linked Sample"
        if self.sampleType & 0x8000 != 0:
            sampleType = "Rom " + sampleType
        
        return "Sample name: <" + self.name + ">. Start: " + str(self.start) + " End: " + str(self.end) + " Loop Start: " + str(self.loopStart) + " Loop End: " + str(self.loopEnd) + " Sample Rate: " + str(self.sampleRate) + " Midi Pitch: " + str(self.midiPitch) + " Pitch Correction: " + str(self.pitchCorrection) + " Sample Link: " + str(self.sampleLink) + " Sample Type: " + sampleType

class SF2ShdrNode(SF2Node):
    # sample pointers
    
    def __init__(self, name, ckID, ckSize, ckData, parent = None):
        SF2Node.__init__(self, name, ckID, ckSize, ckData, parent = None)
        
        self.records = list()
        
        # let's break the information of the pointers
        # how many records are there?
        records = self.ckSize / 46
        for i in range(records):
            baseIndex = i * 46
            name = self.ckData[baseIndex:baseIndex + 20]
            if name.startswith("EOS"):
                # this is the last empty sample... won't add it
                break
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

if __name__ == "__main__":
    # a file name should have been provided to be processed
    
    iFile = open(sys.argv[1], 'ro')
    sf2Tree = SF2Parser.parseFromFile(iFile)
    # let's print some information about the SF2 file
    # engineer
    smpl = sf2Tree.getChild("smpl", True)
    sys.stdout.write(smpl.ckData)
    
    shdr = sf2Tree.getChild("shdr", True)
    sys.stderr.write("There are " + str(shdr.ckSize / 46) + " samples\n")
    
    for record in shdr.records:
        sys.stderr.write("SHDR record : " + str(record) + "\n")
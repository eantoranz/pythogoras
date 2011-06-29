#!/usr/bin/python

# copyright 2011 Edmundo Carmona Antoranz
# This file is released under the terms f Affero GPLv3

import sys
from StringIO import StringIO
from chunk import Chunk

class SF2Parser:
    # this class is used to parse SF2 file contents
    
    @classmethod
    def parseFromFile(cls, iFile):
        # parse a file generating an SF2 tree structure
        
        # read stuff from file at the current position
        aChunk = Chunk(iFile, align=True, bigendian=False)
        ckID = aChunk.getname()
        ckSize = aChunk.getsize()
        ckData = aChunk.read()
        aChunk.close()
        
        # let's create a node from this data
        node = SF2Node(ckID, ckSize, ckData)
        sys.stderr.write("Created node " + str(node) + "\n")
        
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
            someName = node.ckData[0:4] # TODO what is this?
            sys.stderr.write("Some name: " + someName + "\n")
            data = StringIO(node.ckData[4:])
            # let's parse the data until it's empty all children are processed
            try:
                while True:
                    # let's go on until we reach the end of file
                    child = SF2Parser.parseFromFile(data)
                    node.addChild(child)
            except EOFError:
                sys.stderr.write("Reached EOF... coming back a level\n")
                
                

class SF2Node:
    # an SF2 node
    
    def __init__(self, ckID, ckSize, ckData, parent = None):
        (self.ckID, self.ckSize, self.ckData, self.parent) = (ckID, ckSize, ckData, parent)
        self.children = list()
    
    def addChild(self, child):
        # add another child to the SF2 node
        self.children.append(child)
    
    def __str__(self):
        return self.ckID + ". Size " + str(self.ckSize)


if __name__ == "__main__":
    # a file name should have been provided to be processed
    
    iFile = open(sys.argv[1], 'ro')
    sf2Tree = SF2Parser.parseFromFile(iFile)
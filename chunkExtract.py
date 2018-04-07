#!/usr/bin/env python

"""
Extract all stars with given red chunk from ANU format file DumpStar_nn.txt and output
as blank separated file with only field, tile, seq, ra, dec
"""

import sys

def chunkExtract(starFileName, redChunk):
    F = open(starFileName)

    print '# field tile seq ra dec'
    
    while True:
        lcLine = F.readline()
        if len(lcLine)==0:
            break
        fields = lcLine.split(';')
        xChunk = int(fields[7])
        if xChunk == redChunk:
            field = int(fields[0])
            tile = int(fields[1])
            seq = int(fields[2])
            ra = fields[3]
            dec = fields[4]
            outLine = '%d %d %d %s %s' % (field, tile, seq, ra, dec)
            print outLine

if __name__ == "__main__":

    chunkExtract(sys.argv[1], int(sys.argv[2]))

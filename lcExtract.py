#!/usr/bin/env python

"""
Extract a lightcurve from ANU format file, and output
as blank separated file with only t, rmag, rerr, bmag, berr
"""

import sys

def lcExtract(lcFileName, tile, seq, Filter=True):
    F = open(lcFileName)
    Done = False
    Started = False

    print '# t rmag rerr bmag berr obsid'
    
    while not Done:
        lcLine = F.readline()
        if len(lcLine)==0:
            break
        fields = lcLine.split(';')
        xtile = int(fields[2])
        xseq = int(fields[3])
        if xtile==tile and xseq==seq:
            Started = True
            t = float(fields[4])
            rmag = float(fields[9])
            rerr = float(fields[10])
            bmag = float(fields[24])
            berr = float(fields[25])
            obsid = int(fields[5])
            if Filter:
                if (rmag > -15) and (bmag > -15) and (rmag <= -2) and (bmag <= -2) and (rerr < 0.2) and (berr < 0.2):
                    outLine = '%s %s %s %s %s %s' % (fields[4],fields[9],fields[10],fields[24],fields[25],fields[5])
                    print outLine
            else:
                outLine = '%s %s %s %s %s %s' % (fields[4],fields[9],fields[10],fields[24],fields[25],fields[5])
                print outLine
                
        elif Started == True:
            Done = True

if __name__ == "__main__":

    narg = len(sys.argv)-1
    if narg==3:
        lcExtract(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    elif narg==4 and sys.argv[4]=='-n':
        lcExtract(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), Filter=False)

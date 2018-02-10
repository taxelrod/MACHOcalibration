#!/usr/bin/env python
"""
As input, take a F_n.m file containing calibrated photometry information in ANU format
for field n, tile m.

Output a light curve statistics file including for each star in the input file: V and R  
median mag and stdev mag.
"""

import numpy as np
import string
import sys

debug = False

def lcStats(F_fileName, Fstat_fileName):


    fPhot = open(F_fileName)
    fStat = open(Fstat_fileName, 'w')
    eof = False
    activeField = 0
    activeTile = 0

    lcDict = {}
    
    while not eof:
        photLine = fPhot.readline()
        if photLine == '':
            eof = True
        else:
            photFields = string.split(photLine, ';')
            field = int(photFields[1])
            tile = int(photFields[2])
            seq = int(photFields[3])
            rmag = float(photFields[9])
            rerr = float(photFields[10])
            bmag = float(photFields[24])
            rerr = float(photFields[10])
            if field != activeField or tile != activeTile:
                if activeField == 0:
                    activeField = field
                    activeTile = tile
                else:
                    # error exit
                    sys.exit('Input not all same field and tile')
            if lcDict.has_key(seq):
                lc = lcDict[seq]
                lc[0].append(rmag)
                lc[1].append(bmag)
                lcDict[seq] = lc
            else:
                lcDict[seq] = [[rmag], [bmag]]

    if debug:
        print lcDict

    fStat.write('# F T S Rmed Rsigma Vmed Vsigma\n')
    
    for seq in lcDict.keys():
        lc = lcDict[seq]
        lcr = lc[0]
        lcb = lc[1]
        lcrMedian = np.median(lcr)
        lcrStdev = np.std(lcr)
        lcbMedian = np.median(lcb)
        lcbStdev = np.std(lcb)
        outputLine = '%d %d %d %.3f %.3f %.3f %.3f\n' % (field, tile, seq, lcrMedian, lcrStdev, lcbMedian, lcbStdev)
        fStat.write(outputLine)

    fStat.close()
            
if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        sys.exit('Usage: ./lcStats.py F_field.tile outputFile')
    
    lcStats(sys.argv[1], sys.argv[2])
        
        

#!/usr/bin/env python
"""
As input, take a F_n.m file containing photometry information in ANU format
for field n, tile m.

Output a light curve statistics file including for each star in the input file: V and R  
median mag and stdev mag.
"""

import numpy as np
from scipy.stats import pearsonr
import string
import sys

debug = False

def lcStats(F_fileName, Fstat_fileName, filter=True):


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
            berr = float(photFields[25])
            if filter:
                if rmag <= -15 or bmag <= -15 or rmag > -2 or bmag > -2 or rerr < 0 or berr < 0:
                    continue
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
                lc[2].append(rerr)
                lc[3].append(berr)
                lcDict[seq] = lc
            else:
                lcDict[seq] = [[rmag], [bmag], [rerr], [berr]]

    if debug:
        print lcDict

    fStat.write('# F T S Rmed Rsigma RmeanErr Vmed Vsigma VmeanErr WScoeff WScoeffp\n')
    
    for seq in lcDict.keys():
        lc = lcDict[seq]
        lcr = np.array(lc[0])
        lcb = np.array(lc[1])
        lcrerr = lc[2]
        lcberr = lc[3]
        lcrMedian = np.median(lcr)
        lcrStdev = np.std(lcr)
        lcrAverr = np.median(lcrerr)
        lcbMedian = np.median(lcb)
        lcbStdev = np.std(lcb)
        lcbAverr = np.median(lcberr)

        bMinusR = lcb - lcr
        wsCoeff, wsCoeffp = pearsonr(lcb-lcbMedian, lcr-lcrMedian)
        outputLine = '%d %d %d %.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f\n' % (field, tile, seq, lcrMedian, lcrStdev, lcrAverr, lcbMedian, lcbStdev, lcbAverr, wsCoeff, wsCoeffp)
        fStat.write(outputLine)

    fStat.close()
            
if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        sys.exit('Usage: ./lcStats.py F_field.tile outputFile')
    
    lcStats(sys.argv[1], sys.argv[2])
        
        

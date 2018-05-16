#!/usr/bin/env python
"""
As input, take a F_n.m file containing photometry information in ANU format
for field n, tile m.

IT IS ASSUMED THAT ALL DATA IN THE F_n_m FILE IS FOR THE SAME TILE AND FIELD!

Output a light curve statistics file including for each star in the input file: V and R  
median mag and stdev mag.
"""

import numpy as np
from scipy.stats import pearsonr
from statsmodels.robust import mad
import string
import sys
import re
from astropy import units as u
from astropy.coordinates import Angle

debug = False

def lcStats(F_fileName, Fstat_fileName, S_fileName=None, filter=True):


    fPhot = open(F_fileName)
    fStat = open(Fstat_fileName, 'w')
    eof = False
    activeField = 0
    activeTile = 0

    lcDict = {}

    if S_fileName is not None:
        starData = np.loadtxt(S_fileName, delimiter=';',dtype=str)
        sTile = starData[:,1].astype(int)
        sSeq = starData[:,2].astype(int)
        sRchunk = starData[:,7].astype(int)
        raDecPat = re.compile('\(([0-9-\.]+),([0-9-\.]+)\)')
    
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

    if S_fileName is not None:
        fStat.write('# F T S Rchunk RA DEC Rmed Rmad RmeanErr Vmed Vmad VmeanErr WScoeff WScoeffp\n')
    else:
        fStat.write('# F T S Rmed Rmad RmeanErr Vmed Vmad VmeanErr WScoeff WScoeffp\n')

    for seq in lcDict.keys():
        lc = lcDict[seq]
        lcr = np.array(lc[0])
        lcb = np.array(lc[1])
        lcrerr = lc[2]
        lcberr = lc[3]
        lcrMedian = np.median(lcr)
        lcrStdev = mad(lcr, center=lcrMedian)
        lcrAverr = np.median(lcrerr)
        lcbMedian = np.median(lcb)
        lcbStdev = mad(lcb, center=lcbMedian)
        lcbAverr = np.median(lcberr)

        bMinusR = lcb - lcr
        wsCoeff, wsCoeffp = pearsonr(lcb-lcbMedian, lcr-lcrMedian)
        if S_fileName is not None:
            idStar = np.where((sTile==tile) & (sSeq==seq))
            if len(idStar[0])==0:
                print 'Star fts %d %d %d not found in Star file' % (field, tile, seq)
                raise ValueError
            thisStar = starData[idStar,:][0][0]
            redChunk = int(thisStar[7])
            raHMS = Angle(thisStar[3] + ' hours')
            decDMS = Angle(thisStar[4] + ' degrees')
            raDeg = raHMS.degree
            decDeg = decDMS.degree
            outputLine = '%d %d %d %d %.5f %.5f %.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f\n' % (field, tile, seq, redChunk, raDeg, decDeg, lcrMedian, lcrStdev, lcrAverr, lcbMedian, lcbStdev, lcbAverr, wsCoeff, wsCoeffp)
        else:
            outputLine = '%d %d %d %.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f\n' % (field, tile, seq, lcrMedian, lcrStdev, lcrAverr, lcbMedian, lcbStdev, lcbAverr, wsCoeff, wsCoeffp)
        
        fStat.write(outputLine)

    fStat.close()
            
if __name__ == "__main__":
    
    if len(sys.argv) < 3:
        sys.exit('Usage: ./lcStats.py F_field.tile outputFile [DumpStar_nn]')
    
    if len(sys.argv)==3:
        lcStats(sys.argv[1], sys.argv[2])
    else:
        lcStats(sys.argv[1], sys.argv[2], sys.argv[3])
        
        

#!/usr/bin/env python
"""
As input, take a F_n.m file containing photometry information in ANU format
for field n, tile m.

Fit a linear model to lightcurve deviation from median as a function of airmass
"""

import numpy as np
import string
import sys
import statsmodels.api as sm

debug = False
debug2 = False

def detrendAirmass(F_fileName, Fstat_fileName, sigmaThresh, filter=True):


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
            airmass = float(photFields[8])
            rmag = float(photFields[9])
            rerr = float(photFields[10])
            bmag = float(photFields[24])
            berr = float(photFields[25])
            if filter:
                if rmag <= -15 or bmag <= -15 or rmag > -2 or bmag > -2:
                    continue
                if rerr <= 0 or rerr > sigmaThresh or berr <= 0 or berr > sigmaThresh:
                    continue

            if field != activeField or tile != activeTile:
                if activeField == 0:
                    activeField = field
                    activeTile = tile
                else:
                    # error exit
                    sys.exit('Input not all same field and tile')
            if seq in lcDict:
                lc = lcDict[seq]
                lc[0].append(rmag)
                lc[1].append(bmag)
                lc[2].append(rerr)
                lc[3].append(berr)
                lc[4].append(airmass)
                lcDict[seq] = lc
            else:
                lcDict[seq] = [[rmag], [bmag], [rerr], [berr], [airmass]]

    if debug2:
        print(lcDict)


    lcrAll = None

    for seq in list(lcDict.keys()):
        lc = lcDict[seq]
        lcr = lc[0]
        lcb = lc[1]
        lcrerr = lc[2]
        lcberr = lc[3]
        lcairmass = lc[4]
        lcrMedian = np.median(lcr)
        lcrStdev = np.std(lcr)
        lcbMedian = np.median(lcb)
        lcbStdev = np.std(lcb)
        lcColor = np.array(lcb) - np.array(lcr)

        lcr -= lcrMedian
        lcb -= lcbMedian
        if debug:
            print(seq, len(lcr), len(lcairmass))
        if lcrAll is None:
            lcseqAll = np.zeros_like(lcr)
            lcseqAll += seq
            lcrAll = np.array(lcr)
            lcbAll = np.array(lcb)
            lcrerrAll = np.array(lcrerr)
            lcberrAll = np.array(lcberr)
            lcairmassAll = np.array(lcairmass)
            lcColorAll = np.array(lcColor)
        else:
            lcseq = np.zeros_like(lcr)
            lcseq += seq
            lcseqAll = np.concatenate((lcseqAll, lcseq))
            lcrAll = np.concatenate((lcrAll, np.array(lcr)))
            lcbAll = np.concatenate((lcbAll, np.array(lcb)))
            lcrerrAll = np.concatenate((lcrerrAll, np.array(lcrerr)))
            lcberrAll = np.concatenate((lcberrAll, np.array(lcberr)))
            lcairmassAll = np.concatenate((lcairmassAll, np.array(lcairmass)))
            lcColorAll = np.concatenate((lcColorAll, np.array(lcColor)))

    a = lcairmassAll
    a = sm.add_constant(a)
    
    print('Number of points: ', len(lcrAll))
        
    modr_wls = sm.WLS(lcrAll, a, weights=1./(lcrerrAll**2))
    resr_wls = modr_wls.fit()
    fitr = resr_wls.fittedvalues
    print((resr_wls.summary()))

    modb_wls = sm.WLS(lcbAll, a, weights=1./(lcberrAll**2))
    resb_wls = modb_wls.fit()
    fitb = resb_wls.fittedvalues
    print((resb_wls.summary()))

    fStat.write('# seq X R B Rfit Bfit Rerr Berr BmR\n')

    for i in range(len(lcrAll)):
        outputLine = '%d %f %f %f %f %f %f %f %f\n' % (lcseqAll[i], lcairmassAll[i], lcrAll[i], lcbAll[i], fitr[i], fitb[i], lcrerrAll[i], lcberrAll[i], lcColorAll[i])
        fStat.write(outputLine)

    fStat.close()

if __name__ == "__main__":
    
    if len(sys.argv) != 4:
        sys.exit('Usage: ./detrendAirmass.py F_field.tile outputFile sigmaThresh')
    
    detrendAirmass(sys.argv[1], sys.argv[2], float(sys.argv[3]))
        
        

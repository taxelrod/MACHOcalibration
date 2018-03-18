"""
Toy model for MACHO lc calibration with svd
"""
import numpy as np

from numpy.linalg import svd
from numpy.random import randn
from os import path
from copy import deepcopy

import lcScoreBoard

nLc = 0
lcsb = lcScoreBoard.LcScoreBoard()

def loadLcsb(importLcsb):
    global nLc, lcsb

    lcsb = deepcopy(importLcsb)
    nLc = lcsb.nPsf

"""
Return a list of seq numbers for each tile such that each star has the given red chunk
"""
def buildTSlist(dumpStarFileName, redChunk):
    starData = np.loadtxt(dumpStarFileName, delimiter=';', usecols=(1,2,7))
    starData = starData.astype(int)
    tiles = np.unique(starData[:,0])
    nTiles = len(tiles)
    tsList = {}

    for t in tiles:
        idx = np.where((starData[:,0]==t) & (starData[:,2]==redChunk))
        if len(idx[0])>0:
            seqs = starData[idx,1]
            tsList[t] = seqs

    return tsList

# need basically psfAnalysis.loadPsfLcs()
def loadLcFromList(photDir, field, tsList):
    global nLc, lcsb

    for t in tsList.keys():
        # load up full data structure for this tile with np.loadtxt
        photFileName = path.join(photDir, 'F_%d.%d' % (field, t))
        if not path.isfile(photFileName):
            print 'Skipping %s' % photFileName
            continue
        photData = np.loadtxt(photFileName, delimiter=';', usecols=(2,3,4,9,10,24,25,5))
        photTile = np.fix(photData[:,0])
        ibad = np.where(photTile != t)[0]
        if len(ibad) > 0:
            raise ValueError, 'File %s contains data not for tile %d' % (photFileName, t)

        photSeq = np.fix(photData[:,1])
        seqList = tsList[t]
        for s in seqList.flat:
            iseq = np.where(photSeq == s)[0]
            if len(iseq) > 0:
                lcData = np.zeros((len(iseq),6))
                time = lcData[:,0] = photData[iseq,2] # time
                rmag = lcData[:,1] = photData[iseq,3] # rmag
                rerr = lcData[:,2] = photData[iseq,4] # rerr
                bmag = lcData[:,3] = photData[iseq,5] # bmag
                berr = lcData[:,4] = photData[iseq,6] # berr
                obsid = lcData[:,5] = photData[iseq,7] # obsid
                igood = np.where((rmag > -15) & (bmag > -15) & (rmag <= -2) & (bmag <= -2) & (rerr < 0.2) & (berr < 0.2))[0]
                if len(igood) > 0:
                    lcsb.addLC(nLc, lcData[igood,:])
                    nLc += 1


def importLC(lcFileName):

    global nLc, lcsb
    
    lcData = np.loadtxt(lcFileName)
    time = lcData[:,0] # time
    rmag = lcData[:,2] # rmag
    rerr = lcData[:,3] # rerr
    bmag = lcData[:,4] # bmag
    berr = lcData[:,5] # berr
    obsid = lcData[:,1] # obsid

    igood = np.where((rmag > -15) & (bmag > -15) & (rmag <= -2) & (bmag <= -2) & (rerr < 0.2) & (berr < 0.2))[0]
    ngood = len(igood)
#    print lcFileName, lcData.shape[0],ngood
    
    lcDataNew = np.zeros((ngood,6))

    # stupid permutation required - should fix with attached dictionary
    lcDataNew[:,0] = lcData[igood,0] # time
    lcDataNew[:,1] = lcData[igood,2] # rmag
    lcDataNew[:,2] = lcData[igood,3] # rerr
    lcDataNew[:,3] = lcData[igood,4] # bmag
    lcDataNew[:,4] = lcData[igood,5] # berr
    lcDataNew[:,5] = lcData[igood,1] # obsid   
    
    lcsb.addLC(nLc, lcDataNew)
    nLc += 1

"""
Problem:  For large sets of lightcurves, there may be NO time for which all lightcurves are valid.  
Possibly just consider lightcurves with number of valid points > frac of max
"""
def svdLC(minValidFrac=0):
    global nLc, lcsb
  
    t = lcsb.time
    goodT = list()

    validRpts = np.sum(lcsb.validR,axis=1)
    goodLc = np.where(validRpts >= minValidFrac*len(t))[0]
    nGoodLc = len(goodLc)

    print 'svdLC: number of included lightcurves = %d' % nGoodLc

    for (i, tx) in enumerate(t):
        badId = np.where(lcsb.validR[goodLc,i]==False)[0]
        if len(badId)==0:
            goodT.append(i)

    goodT = np.array(goodT)
    nTime = len(goodT)
    lcMatrix = np.zeros((nGoodLc,nTime))

    for i in range(nGoodLc):
        lcMatrix[i,:] = lcsb.rmag[goodLc[i],goodT]
        lcMatrix[i,:] -= np.median(lcMatrix[i,:])

    u, s, v = svd(lcMatrix)

    return goodLc, goodT, u, s, v

def makeApproxLC(u, s, v, nKeep):

    urows = u.shape[0]
    vcols = v.shape[1]
    
    smat = np.zeros((urows, vcols))

    for n in range(nKeep):
        smat[n, n] = s[n]
    lcApprox = np.dot(u, np.dot(smat, v))

    return lcApprox

def diddleLC(a):
    global nLc, lcsb

    for n in range(nLc):
        lcsb.rmag[n,:] += a*(1. + 2*float(n)/float(nLc))*np.sin(lcsb.time[:]/30.)

def diddlerLC(a):
    global nLc, lcsb

    diddler = a*randn(len(lcsb.time[:]))
    
    for n in range(nLc):
        lcsb.rmag[n,:] += diddler

    return diddler

    
def makeCorrectedLC(goodT, u, s, v, nKeep):
    global nLc, lcsb

    lcApprox = makeApproxLC(u, s, v, nKeep)

    lcCorrected = np.zeros_like(lcApprox)

    for n in range(nLc):
        lcCorrected[n,:] = lcsb.rmag[n,goodT] - np.median(lcsb.rmag[n,goodT]) - lcApprox[n,:]

    return lcCorrected

    

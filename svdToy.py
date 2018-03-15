"""
Toy model for MACHO lc calibration with svd
"""
import numpy as np

from numpy.linalg import svd
from numpy.random import randn

import lcScoreBoard

nLc = 0
lcsb = lcScoreBoard.LcScoreBoard()

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


def svdLC():
    global nLc, lcsb
  
    t = lcsb.time
    goodT = list()

    for (i, tx) in enumerate(t):
        badId = np.where(lcsb.validR[:,i]==False)[0]
        if len(badId)==0:
            goodT.append(i)

    goodT = np.array(goodT)
    nTime = len(goodT)
    lcMatrix = np.zeros((nLc,nTime))

    for i in range(nLc):
        lcMatrix[i,:] = lcsb.rmag[i,goodT]
        lcMatrix[i,:] -= np.median(lcMatrix[i,:])

    u, s, v = svd(lcMatrix)

    return goodT, u, s, v

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

    

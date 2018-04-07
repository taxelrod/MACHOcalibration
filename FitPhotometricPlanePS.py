#!/usr/bin/env python

"""
Load a file from the matched Macho lightcurve stats and NSC object file
with columns trimmed to field tile seq Rmed Rsigma Vmed Vsigma rmag rerr imag ierr
This is the PS version with gmag

Fit two planes for rmag gmag
"""

import numpy as np
from scipy.linalg import lstsq
import sys

def FitPhotometricPlane(dataFileName, outputFileName, sigmaClip=5.0, nIterMax=3):
    data = np.loadtxt(dataFileName)
    Rmed = data[:,3]
    Vmed = data[:,5]
    gmag = data[:,8]
    rmag = data[:,10]
    imag = data[:,10]
    unity = np.ones_like(Rmed)
    A = np.stack((Rmed, Vmed, unity), axis=1)

    Aclipped, gmagClipped, gfit = SigmaClipFit(A, gmag, sigmaClip, nIterMax)
    Aclipped, rmagClipped, rfit = SigmaClipFit(A, rmag, sigmaClip)
    Aclipped, gmagClipped, ifit = SigmaClipFit(A, imag, sigmaClip)

    print gfit
    print rfit
    print ifit

    gResid = gfit[0]*Rmed + gfit[1]*Vmed + gfit[2] - gmag
    rResid = rfit[0]*Rmed + rfit[1]*Vmed + rfit[2] - rmag
    iResid = ifit[0]*Rmed + ifit[1]*Vmed + ifit[2] - imag


    nPts, nCols = data.shape
    
    outputFile = open(outputFileName, 'w')
    print >>outputFile, '# F_1 T_1  S_1  Rmed Rsigma Vmed Vsigma angDist gmag gerr rmag rerr imag ierr gresid rresid iresid'
    for n in range(nPts):
        for i in range(nCols):
           print >>outputFile, data[n, i], 
        print >>outputFile, gResid[n], rResid[n], iResid[n]
    outputFile.close()

def SigmaClipFit(a, b, sigmaClip, nIterMax=3):

    nIter = 0
    nClipped = len(b)

    aClipped = a.copy()
    bClipped = b.copy()
    
    while True:
        
        x, residSq, rank, s = lstsq(aClipped, bClipped)

        resid = x[0]*aClipped[:,0] + x[1]*aClipped[:,1] + x[2] - bClipped
        sigma = np.std(resid)

        clipped = np.where(np.abs(resid) > sigmaClip*sigma)[0]
        nClipped = len(clipped)

        if nIter>=nIterMax or nClipped==0:
            break

        aClipped = np.delete(aClipped, clipped, 0)
        bClipped = np.delete(bClipped, clipped, 0)
        nIter += 1
        print nIter, nClipped, aClipped.shape, sigma

    return aClipped, bClipped, x

        
        


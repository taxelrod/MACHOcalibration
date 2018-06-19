#!/usr/bin/env python

"""
Load a file from the matched Macho lightcurve stats and NSC object file
with columns trimmed to field tile seq Rmed Rsigma Vmed Vsigma rmag rerr imag ierr

Fit two planes for rmag gmag
"""

import numpy as np
from scipy.linalg import lstsq
import sys

def FitPhotometricPlane(dataFileName, outputFileName):
    data = np.loadtxt(dataFileName)
    Rmed = data[:,3]
    Vmed = data[:,5]
    rmag = data[:,8]
    imag = data[:,10]
    unity = np.ones_like(Rmed)
    A = np.stack((Rmed, Vmed, unity), axis=1)
    rfit, resid, rank, s = lstsq(A, rmag)
    ifit, resid, rank, s = lstsq(A, imag)

    print(rfit)
    print(ifit)

    rResid = rfit[0]*Rmed + rfit[1]*Vmed + rfit[2] - rmag
    iResid = ifit[0]*Rmed + ifit[1]*Vmed + ifit[2] - imag

    nPts, nCols = data.shape
    
    outputFile = open(outputFileName, 'w')
    print('# F_1 T_1  S_1  Rmed Rsigma Vmed Vsigma angDist rmag rerr imag ierr rresid iresid', file=outputFile)
    for n in range(nPts):
        for i in range(nCols):
           print(data[n, i], end=' ', file=outputFile) 
        print(rResid[n], iResid[n], file=outputFile)
    outputFile.close()
    



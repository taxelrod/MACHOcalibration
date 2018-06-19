#!/usr/bin/env python

"""
Input a lc file, as produced by lcExtract and a wsfit file, as produced
by psfAnalysis, and output a corrected lightcurve
"""
import sys
import numpy as np
from numpy.linalg import lstsq

def lcCorrect(lcFileName, wsFileName):
    lc = np.loadtxt(lcFileName)
    ws = np.loadtxt(wsFileName)

    lctimes = lc[:,0]
    wstimes = ws[:,0]

    rmag = lc[:,1]
    rerr = lc[:,2]
    bmag = lc[:,3]
    berr = lc[:,4]

    dr = ws[:,1]
    db = ws[:,2]

    print('# t rcorr rerr bcorr berr rmag bmag dr db')

    
    for (i,t) in enumerate(lctimes):
        idx = np.where(t==wstimes)[0]
        if len(idx)==0:
            print('Warning time %f not found' % t, file=sys.stderr)
            continue
        else:
            rcorr = rmag[i]+dr[idx]
            bcorr = bmag[i]+db[idx]
            print(t, rcorr[0], rerr[i], bcorr[0], berr[i], rmag[i], bmag[i], dr[idx][0], db[idx][0])


def lstsqFit(lccorrFileName):
    lcDat = np.loadtxt(lccorrFileName)
    nt = lcDat.shape[0]
    A = np.zeros((nt, 2))
    A[:,0] = lcDat[:,8]
    A[:,1] = 1.0
    B = lcDat[:,6]
    x, resid, rank, s = lstsq(A, B)
    return x, resid

    
if __name__ == "__main__":

    lcCorrect(sys.argv[1], sys.argv[2])

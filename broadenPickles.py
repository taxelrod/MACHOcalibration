#!/usr/bin/env python

import sys
import numpy as np

def broadenPickles(picklesFileName, outFileName, lumWidth, measWidth, nSample):
    pickles = np.loadtxt(picklesFileName, dtype=str)
    MachoB = pickles[:,1].astype(float)
    MachoR = pickles[:,2].astype(float)
    DECam_g = pickles[:,3].astype(float)
    DECam_r = pickles[:,4].astype(float)
    DECam_i = pickles[:,5].astype(float)

    deltas = lumWidth*np.random.randn(nSample)

    nrows = pickles.shape[0]

    fOut = open(outFileName, 'w')
    print >>fOut, '# MACHO_B MACHO_R DECam_g DECam_r DECam_i meas_err MACHO_BR DECam_gr DECam_ri'
    
    for n in range(nrows):
        for d in deltas:
            mB = MachoB[n] + d + measWidth*np.random.randn()
            mR = MachoR[n] + d + measWidth*np.random.randn()
            dg = DECam_g[n] + d + measWidth*np.random.randn()
            dr = DECam_r[n] + d + measWidth*np.random.randn()
            di = DECam_i[n] + d + measWidth*np.random.randn()
            print >>fOut, mB, mR, dg, dr, di, measWidth, mB-mR, dg-dr, dr-di

    fOut.close()

if __name__ == "__main__":

    broadenPickles(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]))

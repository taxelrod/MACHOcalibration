#!/usr/bin/env python

import sys
import numpy as np
import synphot
from synphot import units, SourceSpectrum, Observation
from synphot.models import BlackBodyNorm1D
from synphot.spectrum import SpectralElement
import astropy.units as u

def readFilter(filterName):
    bp = SpectralElement.from_file(filterName, wave_unit=u.nm)
    return bp

def calcMag(bp, temp):
    bb = SourceSpectrum(BlackBodyNorm1D, temperature=temp)
    obs = Observation(bb, bp)
    counts = obs.countrate(1.0)
    return -2.5*np.log10(counts.value)

if __name__ == "__main__":

    tMin = 3000.0
    tMax = 20000.0
    tStep = 500.0

    filterDir = sys.argv[1]
    outFileName = sys.argv[2]
    outFile = open(outFileName, 'w')

    bp_MachoB=readFilter(filterDir+'/MACHO_Filter_B.dat')
    bp_MachoR=readFilter(filterDir+'/MACHO_Filter_R.dat')
    bp_DECam_g=readFilter(filterDir+'/DECam_g.dat')
    bp_DECam_r=readFilter(filterDir+'/DECam_r.dat')
    bp_DECam_i=readFilter(filterDir+'/DECam_i.dat')

    print ('# temp MACHO_B MACHO_R DECam_g DECam_r DECam_i',file=outFile)

    temps = np.arange(tMin, tMax, tStep)

    for temp in temps:
        MBmag = calcMag(bp_MachoB, temp)
        MRmag = calcMag(bp_MachoR, temp)
        gmag = calcMag(bp_DECam_g, temp)
        rmag = calcMag(bp_DECam_r, temp)
        imag = calcMag(bp_DECam_i, temp)
        print(temp, MBmag, MRmag, gmag, rmag, imag, file=outFile)


    outFile.close()

    

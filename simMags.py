#!/usr/bin/env python

import sys
import numpy as np
import synphot
from synphot import units, SourceSpectrum, Observation
from synphot.models import BlackBodyNorm1D, Empirical1D
from synphot.spectrum import SpectralElement
from synphot.specio import read_ascii_spec
import astropy.units as u
import os

def readFilter(filterName):
    bp = SpectralElement.from_file(filterName, wave_unit=u.nm)
    return bp

def calcMagFromSpec(bp, specPath):
    sp = SourceSpectrum.from_file(specPath)
    obs = Observation(sp, bp)
    counts = obs.countrate(1.0)
    return -2.5*np.log10(counts.value)

def calcMag(bp, temp):
    bb = SourceSpectrum(BlackBodyNorm1D, temperature=temp)
    obs = Observation(bb, bp)
    counts = obs.countrate(1.0)
    return -2.5*np.log10(counts.value)

def magsVsTemp(filterDir, outFileName):

    tMin = 3000.0
    tMax = 20000.0
    tStep = 500.0

    outFile = open(outFileName, 'w')

    bp_MachoB=readFilter(filterDir+'/MACHO_Filter_B.dat')
    bp_MachoR=readFilter(filterDir+'/MACHO_Filter_R.dat')
    bp_DECam_g=readFilter(filterDir+'/DECam_g.dat')
    bp_DECam_r=readFilter(filterDir+'/DECam_r.dat')
    bp_DECam_i=readFilter(filterDir+'/DECam_i.dat')

    print('# temp MACHO_B MACHO_R DECam_g DECam_r DECam_i',file=outFile)

    temps = np.arange(tMin, tMax, tStep)

    for temp in temps:
        MBmag = calcMag(bp_MachoB, temp)
        MRmag = calcMag(bp_MachoR, temp)
        gmag = calcMag(bp_DECam_g, temp)
        rmag = calcMag(bp_DECam_r, temp)
        imag = calcMag(bp_DECam_i, temp)
        print(temp, MBmag, MRmag, gmag, rmag, imag, file=outFile)


    outFile.close()


def magsPickles(filterDir, picklesDir, outFileName):

    outFile = open(outFileName, 'w')

    bp_MachoB=readFilter(filterDir+'/MACHO_Filter_B.dat')
    bp_MachoR=readFilter(filterDir+'/MACHO_Filter_R.dat')
    bp_DECam_g=readFilter(filterDir+'/DECam_g.dat')
    bp_DECam_r=readFilter(filterDir+'/DECam_r.dat')
    bp_DECam_i=readFilter(filterDir+'/DECam_i.dat')

    print('# spec MACHO_B MACHO_R DECam_g DECam_r DECam_i',file=outFile)

    for f in os.scandir(picklesDir):
        if f.name.endswith('.dat'):
            print(f.path)
            MBmag = calcMagFromSpec(bp_MachoB, f.path)
            MRmag = calcMagFromSpec(bp_MachoR, f.path)
            gmag = calcMagFromSpec(bp_DECam_g, f.path)
            rmag = calcMagFromSpec(bp_DECam_r, f.path)
            imag = calcMagFromSpec(bp_DECam_i, f.path)
            print(f.name, MBmag, MRmag, gmag, rmag, imag, file=outFile)

if __name__ == "__main__":
    magsPickles(sys.argv[1], sys.argv[2], sys.argv[3])

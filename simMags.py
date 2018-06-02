#!/usr/bin/env python

import sys
import numpy as np
import synphot
from synphot import units, SourceSpectrum, Observation, ReddeningLaw
from synphot.models import BlackBodyNorm1D, Empirical1D
from synphot.spectrum import SpectralElement
from synphot.specio import read_ascii_spec
import astropy.units as u
import os

def readFilter(filterName):
    bp = SpectralElement.from_file(filterName, wave_unit=u.nm)
    return bp

def calcMagFromSpec(bp, specPath, redden=None):
    sp = SourceSpectrum.from_file(specPath)
    if redden:
        sp = sp*redden
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
    bp_DECam_g=readFilter(filterDir+'/DECam_noatm_g.dat')
    bp_DECam_r=readFilter(filterDir+'/DECam_noatm_r.dat')
    bp_DECam_i=readFilter(filterDir+'/DECam_noatm_i.dat')

    print('# temp MACHO_B MACHO_R DECam_g DECam_r DECam_i MACHO_BR DECam_gr DECam_ri',file=outFile)

    temps = np.arange(tMin, tMax, tStep)

    for temp in temps:
        MBmag = calcMag(bp_MachoB, temp)
        MRmag = calcMag(bp_MachoR, temp)
        gmag = calcMag(bp_DECam_g, temp)
        rmag = calcMag(bp_DECam_r, temp)
        imag = calcMag(bp_DECam_i, temp)
        print(temp, MBmag, MRmag, gmag, rmag, imag, MBmag-MRmag, gmag-rmag, rmag-imag, file=outFile)


    outFile.close()


def magsPickles(filterDir, picklesDir, outFileName, deltaMachoB=0):

    EBV_LMC = 0.9603 # Schlafly and Finkbeiner LMC average http:..irsa.caltech.edu/applications/DUST (ridiculous!)
    EBV_LMC = 0.2
    extLMC = ReddeningLaw.from_extinction_model('lmcavg').extinction_curve(EBV_LMC)
    
    outFile = open(outFileName, 'w')

    MachoBfactor = 10.0**(-0.4*deltaMachoB)
    bp_MachoB=readFilter(filterDir+'/MACHO_Filter_B.dat') * MachoBfactor
    bp_MachoR=readFilter(filterDir+'/MACHO_Filter_R.dat')
    bp_DECam_g=readFilter(filterDir+'/DECam_noatm_g.dat')
    bp_DECam_r=readFilter(filterDir+'/DECam_noatm_r.dat')
    bp_DECam_i=readFilter(filterDir+'/DECam_noatm_i.dat')
    bp_DECam_z=readFilter(filterDir+'/DECam_z.dat')

    print('# spec MACHO_B MACHO_R DECam_g DECam_r DECam_i DECam_z MACHO_BR DECam_gr DECam_ri DECam_iz',file=outFile)

    for f in os.scandir(picklesDir):
        if f.name.endswith('.dat'):
            print(f.path)
            MBmag = calcMagFromSpec(bp_MachoB, f.path, redden=extLMC)
            MRmag = calcMagFromSpec(bp_MachoR, f.path, redden=extLMC)
            gmag = calcMagFromSpec(bp_DECam_g, f.path, redden=extLMC)
            rmag = calcMagFromSpec(bp_DECam_r, f.path, redden=extLMC)
            imag = calcMagFromSpec(bp_DECam_i, f.path, redden=extLMC)
            zmag = calcMagFromSpec(bp_DECam_z, f.path, redden=extLMC)
            print(f.name, MBmag, MRmag, gmag, rmag, imag, zmag, MBmag-MRmag, gmag-rmag, rmag-imag, imag-zmag, file=outFile)

if __name__ == "__main__":
    nArg = len(sys.argv) -1
    if nArg==3:
        magsPickles(sys.argv[1], sys.argv[2], sys.argv[3])
    elif nArg==4:
        magsPickles(sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]))

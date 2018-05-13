#!/usr/bin/env python
import numpy as np
import pyfits as pf
import sys
from os import path
"""
Given the SMASH catalog as a fits table, and the MACHO fields as an ASCII data file, with
RA and DEC in degrees, extract and write a SMASH catalog for each field
"""

if __name__ == "__main__":

    fieldSize = 42.0/60.0
    
    SMASHcat = sys.argv[1]
    FieldsDat = sys.argv[2]

    SMASHroot, SMASHext = path.splitext(SMASHcat)

    fields = np.loadtxt(FieldsDat)
    fnum = (fields[:,0]).astype(int)
    ra = fields[:,1]
    dec = fields[:,2]
    nFields = len(fnum)

    smash = pf.open(SMASHcat)
    smashData = smash[1].data
    smashRa = smashData['RA']
    smashDec = smashData['DEC']
    
    for i in range(nFields):
        SMASHoutName = SMASHroot + ('_%d' % fnum[i]) + SMASHext
        raLow = ra[i] - 0.5*fieldSize / np.cos(dec[i]*np.pi/180)
        raHi =  ra[i] + 0.5*fieldSize / np.cos(dec[i]*np.pi/180)
        decLow = dec[i] - 0.5*fieldSize
        decHi =  dec[i] + 0.5*fieldSize
        inField = np.where((smashRa>raLow) & (smashRa<raHi) & (smashDec>decLow) & (smashDec<decHi))
        if len(inField[0])>0:
            fieldSmashData = smashData[inField]
            hdu = pf.BinTableHDU(data=fieldSmashData)
            hdu.writeto(SMASHoutName)
            print fnum[i], len(inField[0]), SMASHoutName

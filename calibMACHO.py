#!/usr/bin/env python
"""
As input, take a F_n.m file containing the photometry information in ANU format
for field n, tile m, and DumpStar_n.txt, containing the star information for
field n.

Output a calibrated F_n.m_Cal file in the same ANU format

The input data in column number REPLACE_COL on output is replaced with a value
showing whether the full calibration was done (value=0) or only the generic
zeropoint applied (value=1)

Calibration procedure is based on David Alves' Fortran code, which is in calib_lc4.f, and his data
files in directory CO.

The original Fortran code has been modified to account for exposure times which are not 300 sec, in conformance
with the formulation in the 1999 paper PASP,111,1539
"""

import numpy as np
import string
import calib
import sys

debug = False
REPLACE_COL = 38
def calibPhot(F_fileName, DumpStar_fileName, Fcal_fileName):

    chunkDicts = {}
    fStar = open(DumpStar_fileName)
    eof = False
    while not eof:
        starLine = fStar.readline()
        if starLine == '':
            eof = True
        else:
            starFields = string.split(starLine, ';')
            field = int(starFields[0])
            tile = int(starFields[1])
            seq = int(starFields[2])
            chunk_R_wop = int(starFields[7])
#  if chunkDicts contains tile, then add seq to that dict, else make new one
            if tile not in chunkDicts:
                chunkDicts[tile] = {}
            chunkDict = chunkDicts[tile]
            chunkDict[seq] = chunk_R_wop

    fStar.close()

    if debug:
        for tile in list(chunkDicts.keys()):
            print(tile)
            print(chunkDicts[tile])


    activeField = field

    fPhot = open(F_fileName)
    fCal = open(Fcal_fileName, 'w')
    eof = False
    activeSeq = 0
    activeTile = 0
    
    while not eof:
        photLine = fPhot.readline()
        if photLine == '':
            eof = True
        else:
            photFields = string.split(photLine, ';')
            field = int(photFields[1])
            tile = int(photFields[2])
            seq = int(photFields[3])
            time = float(photFields[4])
            pier = photFields[6]
            exp = float(photFields[7])
            rmag = float(photFields[9])
            rerr = float(photFields[10])
            bmag = float(photFields[24])
            rerr = float(photFields[10])
            if rmag <= -15 or bmag <= -15:
                continue
            if rmag > -2 or bmag > -2:
                continue
            if field != activeField:
                print("Error: fields for %s and %s do not match" % (DumpStar_fileName, F_fileName))
                return
            if tile != activeTile:
                chunkDict = chunkDicts[tile]
            if seq != activeSeq:
                chunk_R_wop = chunkDict[seq]
                (xt,a0,a1,b0,b1,ierr) = calib.get_zps98(field, chunk_R_wop, exp)
                (bje,bjw,bjo) = calib.get_bj(field, chunk_R_wop)
                co = calib.get_co(field, chunk_R_wop)
            	a3 = a0 + co
                a4 = a1 + 0.022*xt
                b3 = b0 + co
                b4 = b1 + 0.004*xt
                activeSeq = seq
                activeTile = tile
            col = bmag - rmag
            if (pier == 'E'):
               dbjit = bje*( col - bjo )
            else:
               dbjit = bjw*( col - bjo )

            omb = bmag + dbjit
            omr = rmag
            omc = omb - omr
            oV = a3 + a4*omc + omb
            oR = b3 + b4*omc + omr
            if debug:
                outputLine = "%d %d %s %f %f %f %f %f %d\n" % (activeTile, activeSeq, pier, time, rmag, bmag, oR, oV, ierr)
            else:
                photFields[9] = '%.3f' % oR
                photFields[24] = '%.3f' % oV
                photFields[REPLACE_COL] = '%d' % ierr
                outputLine = ''
                for (i,field) in enumerate(photFields):
                    if i>0:
                        outputLine += ';' + field
                outputLine += '\n'
            fCal.write(outputLine)

            
if __name__ == "__main__":
    
    if len(sys.argv) != 4:
        sys.exit('Usage: ./calibMACHO.py F_field.tile, DumpStar_field.txt, outputFile')
    
    calibPhot(sys.argv[1], sys.argv[2], sys.argv[3])
        
        

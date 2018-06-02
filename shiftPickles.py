#!/usr/bin/env python

import sys
import numpy as np

def shiftPickles(picklesDat, shift):
    gr = picklesDat[:,8].astype(float) + shift[0]
    ri = picklesDat[:,9].astype(float) + shift[1]
    iz = picklesDat[:,10].astype(float) + shift[2]

    newPickles = picklesDat.copy()
    newPickles[:,8] = gr
    newPickles[:,9] = ri
    newPickles[:,10] = iz

    return newPickles


if __name__ == "__main__":

    picklesFileName = sys.argv[1]
    shift = np.fromstring(sys.argv[2], sep=' ')
    newPicklesFileName = sys.argv[3]

    pickles = np.loadtxt(picklesFileName, dtype=str)

    newPickles = shiftPickles(pickles, shift)

    newPicklesFile = open(newPicklesFileName, 'w')

    print('# spec MACHO_B MACHO_R DECam_g DECam_r DECam_i DECam_z MACHO_BR DECam_gr DECam_ri DECam_iz', file=newPicklesFile)

    nPickles = newPickles.shape[0]
    nCol = newPickles.shape[1]

    for i in range(nPickles):
        for n in range(nCol):
            print(newPickles[i,n], end=' ', file=newPicklesFile)
        print(' ', file=newPicklesFile)

    newPicklesFile.close()
        
    



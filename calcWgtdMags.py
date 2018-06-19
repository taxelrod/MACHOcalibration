#!/usr/bin/env python

import sys
import numpy as np

def calcWgtdMags(matchFileName, outFileName):
    fOut = open(outFileName, 'a')
    
    matchData = np.loadtxt(matchFileName)

    DECam_g = matchData[:,17]
    DECam_gerr = matchData[:,22]
    DECam_r = matchData[:,18]
    DECam_rerr = matchData[:,23]
    DECam_i = matchData[:,19]
    DECam_ierr = matchData[:,24]
    MACHO_R = matchData[:,6]
    MACHO_B = matchData[:,9]
    MACHO_Rerr = matchData[:,8]
    MACHO_Berr = matchData[:,11]

    wgtMACHO_R = np.sum(MACHO_R/MACHO_Rerr)/np.sum(1./MACHO_Rerr)
    wgtMACHO_B = np.sum(MACHO_B/MACHO_Berr)/np.sum(1./MACHO_Berr)
    wgtDECam_g = np.sum(DECam_g/DECam_gerr)/np.sum(1./DECam_gerr)
    wgtDECam_r = np.sum(DECam_r/DECam_rerr)/np.sum(1./DECam_rerr)

    print(wgtMACHO_R, wgtMACHO_B, wgtDECam_g, wgtDECam_r, file=fOut)


    fOut.close()

if __name__ == "__main__":

    calcWgtdMags(sys.argv[1], sys.argv[2])

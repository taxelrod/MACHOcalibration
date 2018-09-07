#!/usr/bin/env python

"""
Calibrates a MACHO lightcurve, either uncompressed or gzip compressed, adding columns
for DECam_r, DECam_g, and their expected uncertainties.  Calibration data is imported
from calibData.
"""

import sys
import numpy as np
import pandas as pd
import re
from io import StringIO
from calibData import calibData

pathRE = re.compile('.*\/F_(\d+)\/.*')

LMC_CMD_split = 0.1   # split in MACHO_V - MACHO_R; separate fits on each side

def usage():
    print('Usage: calcCalibGR inpLC outLC')
    
#
# functions from fitMags.py
#
def reshapeBeta(beta):
    A = np.zeros((2,2))
    A[0,0] = beta[0]
    A[0,1] = 1. - A[0,0]
    A[1,0] = beta[1]
    A[1,1] = 1. - A[1,0]
    B = np.zeros((2,1))
    B[0,0] = beta[2]
    B[1,0] = beta[3]
    return A, B


def fODR(beta, x):
    A, B = reshapeBeta(beta)
    return np.matmul(A, x) + B
#
# function to return integer field num from pathname to xmatch file
#
def parsePathForFieldnum(fieldStr):
    match = pathRE.match(fieldStr)
    return(int(match.group(1)))
    
def loadLightCurve(lcFile, compressType=None):
    #code to load file

    col_names = ['blank', 'field_id', 'tile_id', 'seq_n', 'obs_date', 'obs_id', 'side_of_pier', 'exp_time', 'airmass', 'r_mag', 'r_err', 'r_normsky', 'r_type', 'r_crowd', 'r_chi2', 'r_mpix', 'r_cosmicrf', 'r_amp', 'r_xpix', 'r_ypix', 'r_avesky', 'r_fwhm', 'r_tobs', 'r_cut', 'b_mag', 'b_err', 'b_normsky', 'b_type', 'b_crowd', 'b_chi2', 'b_mpix', 'b_cosmicrf', 'b_amp', 'b_xpix', 'b_ypix', 'b_avesky', 'b_fwhm', 'b_tobs', 'b_cut']

    use_cols = ['field_id', 'tile_id', 'seq_n', 'obs_date', 'obs_id', 'r_mag', 'r_err', 'b_mag', 'b_err']

    data = pd.read_csv(lcFile,sep=';', names=col_names, usecols=use_cols, compression=compressType, na_filter=False)

    return data


if __name__ == "__main__":

    narg = len(sys.argv)
    if narg==3:
        lcFile = sys.argv[1]
        lcOutFile = sys.argv[2]
    else:
        usage()
        raise ValueError

    if lcFile.endswith('.gz'):
        compressType = 'gzip'
    else:
        compressType = None

    lcData = loadLightCurve(lcFile, compressType)

    calFile = StringIO(calibData())
    photdf = pd.read_csv(calFile,sep=' ')
#
# parse field number from field path entry
#
    photdf['field']=photdf['field'].apply(parsePathForFieldnum)

    fieldTarget = lcData['field_id'][0]
    fieldCalInfo = photdf[photdf.field==fieldTarget]

    if len(fieldCalInfo) == 0:
        print('Field %d not in calibration database' % fieldTarget)
        raise ValueError
    else:
        print('Using calibration data for field %d' % fieldTarget)

    betaRed = np.array([fieldCalInfo.rdbetag.values[0], fieldCalInfo.rdbetar.values[0], fieldCalInfo.rdzpg.values[0], fieldCalInfo.rdzpr.values[0]])
    betaBlue = np.array([fieldCalInfo.blbetag.values[0], fieldCalInfo.blbetar.values[0], fieldCalInfo.blzpg.values[0], fieldCalInfo.blzpr.values[0]])

#    print('betaRed: ', betaRed)
#    print('betaBlue: ', betaBlue)

#
# iterate over lcData - use .apply
#

    lcValid = lcData[(lcData.b_mag != -99) & (lcData.r_mag != -99)].copy()
    nValidPts = lcValid.shape[0]
    cal_r = np.zeros(nValidPts)
    cal_g = np.zeros(nValidPts)
    cal_r_err = np.zeros(nValidPts)
    cal_g_err = np.zeros(nValidPts)

    i = 0
    for lcPoint in lcValid.iterrows():
       MACHO_V = lcPoint[1]['b_mag']
       MACHO_R = lcPoint[1]['r_mag']
       MACHO_Verr = lcPoint[1]['b_err']
       MACHO_Rerr = lcPoint[1]['r_err']

       if MACHO_V - MACHO_R > LMC_CMD_split:
            cal_Red = fODR(betaRed, np.vstack((MACHO_R, MACHO_V)))
            cal_g[i] = cal_Red[0,0]
            cal_r[i] = cal_Red[1,0]
            cal_g_err[i] = np.sqrt(((1-betaRed[0])*MACHO_Rerr)**2 + (betaRed[0]*MACHO_Verr)**2)
            cal_r_err[i] = np.sqrt(((1-betaRed[1])*MACHO_Rerr)**2 + (betaRed[1]*MACHO_Verr)**2)
       else:
            cal_Blue = fODR(betaBlue, np.vstack((MACHO_R, MACHO_V)))
            cal_g[i] = cal_Blue[0,0]
            cal_r[i] = cal_Blue[1,0]
            cal_g_err[i] = np.sqrt(((1-betaBlue[0])*MACHO_Rerr)**2 + (betaBlue[0]*MACHO_Verr)**2)
            cal_r_err[i] = np.sqrt(((1-betaBlue[1])*MACHO_Rerr)**2 + (betaBlue[1]*MACHO_Verr)**2)

       i += 1

    lcValid['DECam_r'] = cal_r
    lcValid['DECam_g'] = cal_g
    lcValid['DECam_r_err'] = cal_r_err
    lcValid['DECam_g_err'] = cal_g_err
    
    if lcOutFile.endswith('.gz'):
        compressType = 'gzip'
    else:
        compressType = None

    lcValid.to_csv(lcOutFile, sep=';', index=False, float_format='%.4f', compression=compressType)


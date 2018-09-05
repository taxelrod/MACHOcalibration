#!/usr/bin/env python

import sys
import numpy as np
import pandas as pd
import re
from io import StringIO
from calibData import calibData

pathRE = re.compile('.*\/F_(\d+)\/.*')

LMC_CMD_split = 0.1   # split in MACHO_V - MACHO_R; separate fits on each side

def usage():
    print('you screwed up!')
    
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
    
def loadLightCurve(lcFile):
    #code to load file

    col_names = ['blank', 'field_id', 'tile_id', 'seq_n', 'obs_date', 'obs_id', 'side_of_pier', 'exp_time', 'airmass', 'r_mag', 'r_err', 'r_normsky', 'r_type', 'r_crowd', 'r_chi2', 'r_mpix', 'r_cosmicrf', 'r_amp', 'r_xpix', 'r_ypix', 'r_avesky', 'r_fwhm', 'r_tobs', 'r_cut', 'b_mag', 'b_err', 'b_normsky', 'b_type', 'b_crowd', 'b_chi2', 'b_mpix', 'b_cosmicrf', 'b_amp', 'b_xpix', 'b_ypix', 'b_avesky', 'b_fwhm', 'b_tobs', 'b_cut']

    use_cols = ['field_id', 'tile_id', 'seq_n', 'obs_date', 'obs_id', 'r_mag', 'r_err', 'b_mag', 'b_err']

    data = pd.read_csv(lcFile,sep=';', names=col_names, usecols=use_cols, compression='gzip', na_filter=False)

    return data


if __name__ == "__main__":

    narg = len(sys.argv)
    if narg==4:
        fieldTarget = int(sys.argv[1])
        MACHO_R = float(sys.argv[2])
        MACHO_V = float(sys.argv[3])
        # make a one row dataframe
    elif narg==3:
        lcFile = sys.argv[1]
        lcData = loadLightCurve(lcFile)
    else:
        usage()
        raise ValueError

    calFile = StringIO(calibData())
    photdf = pd.read_csv(calFile,sep=' ')
#
# parse field number from field path entry
#
    photdf['field']=photdf['field'].apply(parsePathForFieldnum)

    fieldTarget = 77  # DEBUG
    fieldCalInfo = photdf[photdf.field==fieldTarget]
#
# iterate over lcData
#
    for lcPoint in lcData.iterrows():
       MACHO_V = lcPoint[1]['b_mag']
       MACHO_R = lcPoint[1]['r_mag']

       if MACHO_V - MACHO_R > LMC_CMD_split:
            betaRed = np.array([fieldCalInfo.rdbetag.values[0], fieldCalInfo.rdbetar.values[0], fieldCalInfo.rdzpg.values[0], fieldCalInfo.rdzpr.values[0]])
            cal_Red = fODR(betaRed, np.vstack((MACHO_R, MACHO_V)))
            cal_g = cal_Red[0,0]
            cal_r = cal_Red[1,0]
       else:
            betaBlue = np.array([fieldCalInfo.blbetag.values[0], fieldCalInfo.blbetar.values[0], fieldCalInfo.blzpg.values[0], fieldCalInfo.blzpr.values[0]])
            cal_Blue = fODR(betaBlue, np.vstack((MACHO_R, MACHO_V)))
            cal_g = cal_Blue[0,0]
            cal_r = cal_Blue[1,0]

       print(cal_r, cal_g)


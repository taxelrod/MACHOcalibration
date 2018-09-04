#!/usr/bin/env python

import sys
import numpy as np
import pandas as pd
import re

pathRE = re.compile('.*\/F_(\d+)\/.*')

LMC_CMD_split = 0.1   # split in MACHO_V - MACHO_R; separate fits on each side

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
    
if __name__ == "__main__":

    fieldTarget = int(sys.argv[1])
    MACHO_R = float(sys.argv[2])
    MACHO_V = float(sys.argv[3])
    calFile = sys.argv[4]

    photdf=pd.read_csv(calFile,sep=' ')
#
# parse field number from field path entry
#
    photdf['field']=photdf['field'].apply(parsePathForFieldnum)

    fieldCalInfo = photdf[photdf.field==fieldTarget]

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


    

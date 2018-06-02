#!/usr/bin/env python

import sys
import numpy as np
import statsmodels.api as sm
import scipy.odr as odr

useODR = False

def fODR(B, x):
    return B[0]*x[0,:] + B[1]*x[1,:] + B[2]

def fitODR(y, yerr, x1, x1err, x2, x2err):
    x = np.vstack((x1, x2))
    sx = np.vstack((x1err, x2err))
    sy = yerr
    odrData = odr.RealData(x, y, sx=sx, sy=sy)
    odrLin = odr.Model(fODR)
    odrModel = odr.ODR(odrData, odrLin, beta0=[0,0,0])
    res=odrModel.run()
    return res.beta, res.sd_beta

def fitPlane(z, zerr, x, y):
    # form x, y, and vector of ones into a matrix
    nPts = len(z)
    if len(x) != nPts or len(y) != nPts:
        sys.exit('fitPlane input vectors must all have same length')
    a = np.column_stack((x, y))
    a = sm.add_constant(a)

    mod_wls = sm.WLS(z, a, weights=1./zerr)
    res_wls = mod_wls.fit()
    return res_wls.params, res_wls.bse, res_wls.resid
#    print(res_wls.summary())

def fitQuad(z, zerr, x, y):
    # form x, y, and vector of ones into a matrix
    nPts = len(z)
    if len(x) != nPts or len(y) != nPts:
        sys.exit('fitPlane input vectors must all have same length')
    a = np.column_stack((x, y, x*x, y*y))
    a = sm.add_constant(a)

    mod_wls = sm.WLS(z, a, weights=1./zerr)
    res_wls = mod_wls.fit()
    print(res_wls.summary())


def fitMags(outmag, magerr, mag, color):
    # form x, y, and vector of ones into a matrix
    nPts = len(outmag)
    if len(mag) != nPts or len(color) != nPts:
        sys.exit('fitPlane input vectors must all have same length')
    a = np.column_stack((mag, color, color*color, color*color*color))
    a = sm.add_constant(a)

    mod_wls = sm.WLS(outmag, a, weights=1./magerr)
    res_wls = mod_wls.fit()
    print(res_wls.summary())
    print 'MSE_resid:', res_wls.mse_resid

if __name__ == "__main__":

    matchFileName = sys.argv[1]
    outFileName = sys.argv[2]

    fOut = open(outFileName, 'a')
    
    matchData = np.loadtxt(matchFileName)
    DECam_g = matchData[:,17]
    DECam_gerr = matchData[:,22]
    DECam_r = matchData[:,18]
    DECam_rerr = matchData[:,23]
    DECam_i = matchData[:,19]
    DECam_ierr = matchData[:,24]
    MACHO_R = matchData[:,6]
    MACHO_V = matchData[:,9]
    MACHO_Rerr = matchData[:,8]
    MACHO_Verr = matchData[:,11]

    if useODR:
        (beta_g, sd_beta_g) = fitODR(DECam_g, DECam_gerr, MACHO_R, MACHO_Rerr, MACHO_V, MACHO_Verr)
        (beta_r, sd_beta_r) = fitODR(DECam_r, DECam_rerr, MACHO_R, MACHO_Rerr, MACHO_V, MACHO_Verr)
        (beta_i, sd_beta_i) = fitODR(DECam_i, DECam_ierr, MACHO_R, MACHO_Rerr, MACHO_V, MACHO_Verr)

    else:
        (beta_g, sd_beta_g, resid_g) = fitPlane(DECam_g, DECam_gerr, MACHO_R, MACHO_V)
        (beta_r, sd_beta_r, resid_r) = fitPlane(DECam_r, DECam_rerr, MACHO_R, MACHO_V)
        (beta_i, sd_beta_i, resid_i) = fitPlane(DECam_i, DECam_ierr, MACHO_R, MACHO_V)

    print >>fOut, matchFileName, beta_g, sd_beta_g, beta_r, sd_beta_r, beta_i, sd_beta_i
#    print >>fOut, resid_g
#    print >>fOut, resid_r
#    print >>fOut, resid_i

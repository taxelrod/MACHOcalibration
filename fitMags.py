#!/usr/bin/env python

import sys
import numpy as np
import statsmodels.api as sm
import scipy.odr as odr

useODR = True
threeD = False
matchFmt = True
grMax = 1.4

if threeD:
    lenY = 3
else:
    lenY = 2
lenX = 2

def reshapeBeta(beta):
    A = np.reshape(beta[0:-lenY], (lenY, lenX))
    B = np.reshape(beta[lenX*lenY:], (lenY,1))
    return A, B

def fODR(Beta, x):
    A, B = reshapeBeta(Beta)
    return np.matmul(A, x) + B

def fitODR(y, yerr, x, xerr):
    odrData = odr.RealData(x, y, sx=xerr, sy=yerr)
    odrLin = odr.Model(fODR)
    odrModel = odr.ODR(odrData, odrLin, beta0=np.zeros((lenY*lenX + lenY)), maxit=1000)
    res=odrModel.run()
    res.pprint()
    return res.beta, res.sd_beta, res.cov_beta, res.res_var

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

def printFlattened(arr, file):
    flatArr = arr.flatten()
    nElem = len(flatArr)
    for n in range(nElem):
        print >>file, flatArr[n],
    print >>file, ''
    
if __name__ == "__main__":

    matchFileName = sys.argv[1]
    outFileName = sys.argv[2]
    outSynthFileName = sys.argv[3]

    fOut = open(outFileName, 'a')
    sys.stdout = fOut
    
    print >>fOut, matchFileName
    matchData = np.loadtxt(matchFileName)
    if matchFmt:
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
    else:
        DECam_g = matchData[:,2]
        DECam_r = matchData[:,3]
        DECam_i = matchData[:,4]
        DECam_gr = matchData[:,6]
        MACHO_R = matchData[:,1]
        MACHO_V = matchData[:,0]
        meas_err = matchData[:,5]

        filt_gr = np.where(DECam_gr < grMax)
        DECam_g = DECam_g[filt_gr]
        DECam_r = DECam_r[filt_gr]
        DECam_i = DECam_i[filt_gr]
        MACHO_V = MACHO_V[filt_gr]
        MACHO_R = MACHO_R[filt_gr]
        meas_err = meas_err[filt_gr]
        MACHO_Rerr = MACHO_Verr = DECam_gerr = DECam_rerr = DECam_ierr = meas_err        

    if useODR:
        if threeD:
            (beta, sd_beta, cov_beta, res_var) = fitODR(np.vstack((DECam_g, DECam_r, DECam_i)), np.vstack((DECam_gerr, DECam_rerr, DECam_ierr)), np.vstack((MACHO_R, MACHO_V)), np.vstack((MACHO_Rerr, MACHO_Verr)))
        else:
            (beta, sd_beta, cov_beta, res_var) = fitODR(np.vstack((DECam_g, DECam_r)), np.vstack((DECam_gerr, DECam_rerr)), np.vstack((MACHO_R, MACHO_V)), np.vstack((MACHO_Rerr, MACHO_Verr)))
            synth_gr = fODR(beta, np.vstack((MACHO_R, MACHO_V)))
            synth_g = synth_gr[0,:]
            synth_r = synth_gr[1,:]

            nPts = len(synth_g)
            outData = np.zeros((nPts, 10))
            outData[:,0] = DECam_g
            outData[:,1] = DECam_gerr
            outData[:,2] = DECam_r
            outData[:,3] = DECam_rerr
            outData[:,4] = MACHO_R
            outData[:,5] = MACHO_Rerr
            outData[:,6] = MACHO_V
            outData[:,7] = MACHO_Verr
            outData[:,8] = synth_g.transpose()
            outData[:,9] = synth_r.transpose()
            np.savetxt(outSynthFileName, outData, header='DECam_g DECam_gerr DECam_r DECam_rerr MACHO_R MACHO_Rerr MACHO_B MACHO_Berr synth_g synth_r')
            
            
#        A, B = reshapeBeta(beta)
#        printFlattened(A, fOut)
#        printFlattened(B, fOut)
#        A, B = reshapeBeta(sd_beta)
#        printFlattened(A, fOut)
#        printFlattened(B, fOut)
#        printFlattened(cov_beta, fOut)
        print >>fOut, np.sqrt(res_var/(3.*len(DECam_g)))
    else:
        (beta_g, sd_beta_g, resid_g) = fitPlane(DECam_g, DECam_gerr, MACHO_R, MACHO_V)
        (beta_r, sd_beta_r, resid_r) = fitPlane(DECam_r, DECam_rerr, MACHO_R, MACHO_V)
        (beta_i, sd_beta_i, resid_i) = fitPlane(DECam_i, DECam_ierr, MACHO_R, MACHO_V)
        print >>fOut, matchFileName, beta_g, sd_beta_g, beta_r, sd_beta_r, beta_i, sd_beta_i
#    print >>fOut, resid_g
#    print >>fOut, resid_r
#    print >>fOut, resid_i

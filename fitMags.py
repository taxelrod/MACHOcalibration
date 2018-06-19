#!/usr/bin/env python

import sys
import numpy as np
import statsmodels.api as sm
import scipy.odr as odr

threeD = False
matchFmt = True
grMax = 1.4
nIter = 5
nSigma = 3


if threeD:
    lenY = 3
else:
    lenY = 2
lenX = 2

def dist3D(x0, x1, x2):
    # minimum distance from x0 to the line formed by x1 and x2.  All coords are 2D or 3D.
    # see http://mathworld.wolfram.com/Point-LineDistance3-Dimensional.html

    vec = np.cross(np.cross(x2 - x1, x1 - x0), x1-x2)
    uvec = vec/np.linalg.norm(vec)
    dist = np.linalg.norm(np.cross(x2 - x1, x1 - x0))/np.linalg.norm(x2-x1)

    return dist, dist*uvec

def filterOnDist(DECam_g, synth_g, nSigma):
    x1 = np.array([10.0, 10.0, 0])
    x2 = np.array([30.0, 30.0, 0])

    dist = np.zeros_like(DECam_g)

    for (i, dg) in enumerate(DECam_g):
        sg = synth_g[i]
        x0 = np.array([dg, sg, 0])
        d, dvec = dist3D(x0, x1, x2)
        dist[i] = d

    sigma = np.std(dist)
    goodId = np.where(dist<nSigma*sigma)
    return goodId
                         
        

def reshapeBeta(beta):
    if threeD:
        A = np.reshape(beta[0:-lenY], (lenY, lenX))
        B = np.reshape(beta[lenX*lenY:], (lenY,1))
    else:
        A = np.zeros((2,2))
        A[0,0] = beta[0]
        A[0,1] = 1. - A[0,0]
        A[1,0] = beta[1]
        A[1,1] = 1. - A[1,0]
        B = np.zeros((2,1))
        B[0,0] = beta[2]
        B[1,0] = beta[3]
    return A, B


def fODR(Beta, x):
    A, B = reshapeBeta(Beta)
    return np.matmul(A, x) + B

def fitODR(y, yerr, x, xerr):
    odrData = odr.RealData(x, y, sx=xerr, sy=yerr)
    odrLin = odr.Model(fODR)
    if threeD:
        odrModel = odr.ODR(odrData, odrLin, beta0=np.zeros((lenY*lenX + lenY)))
    else:
        odrModel = odr.ODR(odrData, odrLin, beta0=np.zeros((4)))
    res=odrModel.run()
    res.pprint()
    return res.beta, res.sd_beta, res.cov_beta, res.res_var


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

    goodId = range(len(DECam_g))   #  all good to begin
    print >>fOut, -1, len(DECam_g)
    
    for n in range(nIter):
        if threeD:
            (beta, sd_beta, cov_beta, res_var) = fitODR(np.vstack((DECam_g, DECam_r, DECam_i)), np.vstack((DECam_gerr, DECam_rerr, DECam_ierr)), np.vstack((MACHO_R, MACHO_V)), np.vstack((MACHO_Rerr, MACHO_Verr)))
        else:
            (beta, sd_beta, cov_beta, res_var) = fitODR(np.vstack((DECam_g[goodId], DECam_r[goodId])), np.vstack((DECam_gerr[goodId], DECam_rerr[goodId])), np.vstack((MACHO_R[goodId], MACHO_V[goodId])), np.vstack((MACHO_Rerr[goodId], MACHO_Verr[goodId])))
            synth_gr = fODR(beta, np.vstack((MACHO_R, MACHO_V)))
            synth_g = synth_gr[0,:]
            synth_r = synth_gr[1,:]
            goodId = filterOnDist(DECam_g, synth_g, nSigma)
            print >>fOut, n, len(goodId[0])
                   

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
    print >>fOut, np.sqrt(res_var/(3.*len(DECam_g)))


#        A, B = reshapeBeta(beta)
#        printFlattened(A, fOut)
#        printFlattened(B, fOut)
#        A, B = reshapeBeta(sd_beta)
#        printFlattened(A, fOut)
#        printFlattened(B, fOut)
#        printFlattened(cov_beta, fOut)
#    print >>fOut, resid_g
#    print >>fOut, resid_r
#    print >>fOut, resid_i

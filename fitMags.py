#!/usr/bin/env python

import sys
import numpy as np
import scipy.odr as odr

threeD = False
matchFmt = True
grMax = 1.4
nIter = 5
nSigma = 1.5
LMC_CMD_split = 0.1   # split in MACHO_V - MACHO_R; separate fits on each side


if threeD:
    lenY = 3
else:
    lenY = 2
lenX = 2

def mad(x):
    return np.median(np.abs(x - np.median(x))
                     
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

    sigma = mad(dist)
    goodId = np.where(dist<nSigma*sigma)
    print('filterOnDist', np.mean(dist), sigma, len(DECam_g), len(goodId[0]))
    return goodId[0]
                         
        

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
    return res.beta, res.sd_beta, res.cov_beta, res.sum_square


def printFlattened(arr, file):
    flatArr = arr.flatten()
    nElem = len(flatArr)
    for n in range(nElem):
        print(flatArr[n], end=' ', file=file)
    print('', file=file)
    
if __name__ == "__main__":

    matchFileName = sys.argv[1]
    outFileName = sys.argv[2]
    outSynthFileName = sys.argv[3]

    fOut = open(outFileName, 'w')
    sys.stdout = fOut
    
    print(matchFileName, file=fOut)
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
        F = matchData[:,0]
        T = matchData[:,1]
        S = matchData[:,2]
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

    print(-1, 'Total number of points:', len(DECam_g), file=fOut)

# Blue side of CMD split

    goodIdBlue = np.where(MACHO_V - MACHO_R < LMC_CMD_split)
    DECam_g_Blue = DECam_g[goodIdBlue]
    DECam_r_Blue = DECam_r[goodIdBlue]
    DECam_gerr_Blue = DECam_gerr[goodIdBlue]
    DECam_rerr_Blue = DECam_rerr[goodIdBlue]
    MACHO_V_Blue = MACHO_V[goodIdBlue]
    MACHO_R_Blue = MACHO_R[goodIdBlue]
    MACHO_Verr_Blue = MACHO_Verr[goodIdBlue]
    MACHO_Rerr_Blue = MACHO_Rerr[goodIdBlue]
    F_Blue = F[goodIdBlue]
    T_Blue = T[goodIdBlue]
    S_Blue = S[goodIdBlue]
    goodId = list(range(len(DECam_g_Blue))) #  all good to begin
    
    print(-1, 'Total number of blue points:', len(goodId), file=fOut)
    
    for n in range(nIter):
        if threeD:
            (beta, sd_beta, cov_beta, res_var) = fitODR(np.vstack((DECam_g, DECam_r, DECam_i)), np.vstack((DECam_gerr, DECam_rerr, DECam_ierr)), np.vstack((MACHO_R, MACHO_V)), np.vstack((MACHO_Rerr, MACHO_Verr)))
        else:
            (beta, sd_beta, cov_beta, sum_square) = fitODR(np.vstack((DECam_g_Blue[goodId], DECam_r_Blue[goodId])), np.vstack((DECam_gerr_Blue[goodId], DECam_rerr_Blue[goodId])), np.vstack((MACHO_R_Blue[goodId], MACHO_V_Blue[goodId])), np.vstack((MACHO_Rerr_Blue[goodId], MACHO_Verr_Blue[goodId])))
            synth_gr = fODR(beta, np.vstack((MACHO_R[goodIdBlue], MACHO_V[goodIdBlue])))
            synth_g = synth_gr[0,:]
            synth_r = synth_gr[1,:]
            calErr_g_blue = synth_g - DECam_g[goodIdBlue]
            calErr_r_blue = synth_r - DECam_r[goodIdBlue]
            goodId_g = filterOnDist(DECam_g_Blue, synth_g, nSigma)
            goodId_r = filterOnDist(DECam_r_Blue, synth_r, nSigma)
            goodId = np.unique(np.concatenate((goodId_g,goodId_r)))
            print(n, len(goodId), file=fOut)

    synth_g_blue = synth_g
    synth_r_blue = synth_r

    print('std calib error (g, r): ', mad(calErr_g_blue), mad(calErr_r_blue), file=fOut)
    
# Red side of CMD split

    goodIdRed = np.where(MACHO_V - MACHO_R >= LMC_CMD_split)
    DECam_g_Red = DECam_g[goodIdRed]
    DECam_r_Red = DECam_r[goodIdRed]
    DECam_gerr_Red = DECam_gerr[goodIdRed]
    DECam_rerr_Red = DECam_rerr[goodIdRed]
    MACHO_V_Red = MACHO_V[goodIdRed]
    MACHO_R_Red = MACHO_R[goodIdRed]
    MACHO_Verr_Red = MACHO_Verr[goodIdRed]
    MACHO_Rerr_Red = MACHO_Rerr[goodIdRed]
    F_Red = F[goodIdRed]
    T_Red = T[goodIdRed]
    S_Red = S[goodIdRed]
    goodId = list(range(len(DECam_g_Red))) #  all good to begin

    print(-1, 'Total number of red points:', len(goodId), file=fOut)
    
    for n in range(nIter):
        if threeD:
            (beta, sd_beta, cov_beta, res_var) = fitODR(np.vstack((DECam_g, DECam_r, DECam_i)), np.vstack((DECam_gerr, DECam_rerr, DECam_ierr)), np.vstack((MACHO_R, MACHO_V)), np.vstack((MACHO_Rerr, MACHO_Verr)))
        else:
            (beta, sd_beta, cov_beta, sum_square) = fitODR(np.vstack((DECam_g_Red[goodId], DECam_r_Red[goodId])), np.vstack((DECam_gerr_Red[goodId], DECam_rerr_Red[goodId])), np.vstack((MACHO_R_Red[goodId], MACHO_V_Red[goodId])), np.vstack((MACHO_Rerr_Red[goodId], MACHO_Verr_Red[goodId])))
            synth_gr = fODR(beta, np.vstack((MACHO_R[goodIdRed], MACHO_V[goodIdRed])))
            synth_g = synth_gr[0,:]
            synth_r = synth_gr[1,:]
            calErr_g_red = synth_g - DECam_g[goodIdRed]
            calErr_r_red = synth_r - DECam_r[goodIdRed]
            goodId_g = filterOnDist(DECam_g_Red, synth_g, nSigma)
            goodId_r = filterOnDist(DECam_r_Red, synth_r, nSigma)
            goodId = np.unique(np.concatenate((goodId_g,goodId_r)))
            print(n, len(goodId), file=fOut)
                   

    synth_g_full = np.concatenate((synth_g_blue, synth_g))
    synth_r_full = np.concatenate((synth_r_blue, synth_r))
    
    print('std calib error (g, r): ', mad(calErr_g_red), mad(calErr_r_red), file=fOut)
    
    nPts = len(synth_g_full)
    outData = np.zeros((nPts, 13))
    outData[:,0] = np.concatenate((DECam_g_Blue, DECam_g_Red))
    outData[:,1] = np.concatenate((DECam_gerr_Blue, DECam_gerr_Red))
    outData[:,2] = np.concatenate((DECam_r_Blue, DECam_r_Red))
    outData[:,3] = np.concatenate((DECam_rerr_Blue, DECam_rerr_Red))
    outData[:,4] = np.concatenate((MACHO_R_Blue, MACHO_R_Red))
    outData[:,5] = np.concatenate((MACHO_Rerr_Blue, MACHO_Rerr_Red))
    outData[:,6] = np.concatenate((MACHO_V_Blue, MACHO_V_Red))
    outData[:,7] = np.concatenate((MACHO_Verr_Blue, MACHO_Verr_Red))
    outData[:,8] = synth_g_full.transpose()
    outData[:,9] = synth_r_full.transpose()
    outData[:,10] = np.concatenate((F_Blue, F_Red))
    outData[:,11] = np.concatenate((T_Blue, T_Red))
    outData[:,12] = np.concatenate((S_Blue, S_Red))
    np.savetxt(outSynthFileName, outData, header='DECam_g DECam_gerr DECam_r DECam_rerr MACHO_R MACHO_Rerr MACHO_B MACHO_Berr synth_g synth_r F T S')  

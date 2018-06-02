#!/usr/bin/env python

import sys
import numpy as np
#import statsmodels.api as sm

"""
Fit output of synthetic photometry file generated from Pickls models by simMags.py to a line
in 3D color space (g-r, r-i, i-z)
"""

def fitPickles(picklesFileName):
    pickles = np.loadtxt(picklesFileName, dtype=str)
    gr = pickles[:,8].astype(float)
    ri = pickles[:,9].astype(float)
    iz = pickles[:,10].astype(float)


# Code adapted from https://stackoverflow.com/questions/2298390/fitting-a-line-in-3d

    data = np.concatenate((gr[:, np.newaxis], 
                           ri[:, np.newaxis], 
                           iz[:, np.newaxis]), 
                          axis=1)


    # Calculate the mean of the points, i.e. the 'center' of the cloud
    datamean = data.mean(axis=0)

    # Do an SVD on the mean-centered data.
    uu, dd, vv = np.linalg.svd(data - datamean)

    # Now vv[0] contains the first principal component, i.e. the direction
    # vector of the 'best fit' line in the least squares sense.

    # Now generate some points along this best fit line, for plotting.

    # I use -7, 7 since the spread of the data is roughly 14
    # and we want it to have mean 0 (like the points we did
    # the svd on). Also, it's a straight line, so we only need 2 points.
    linepts = vv[0] * np.mgrid[-7:7:2j][:, np.newaxis]

    # shift by the mean to get the line in the right place
    linepts += datamean

    return vv[0], linepts

def dist3D(x0, x1, x2):
    # minimum distance from x1 to the line formed by x1 and x2.  All coords are 3D.
    # see http://mathworld.wolfram.com/Point-LineDistance3-Dimensional.html

    vec = np.cross(np.cross(x2 - x1, x1 - x0), x1-x2)
    uvec = vec/np.linalg.norm(vec)
    dist = np.linalg.norm(np.cross(x2 - x1, x1 - x0))/np.linalg.norm(x2-x1)

    return dist, dist*uvec

def addDist3D(pts, matchFileName, outFileName, unMatchedFmt=False):
    x1 = pts[0]
    x2 = pts[1]

    outFile = open(outFileName, 'w')
    matchDat = np.loadtxt(matchFileName, dtype=str)
    
    if unMatchedFmt:
        print('# RA DEC U G R I Z UERR GERR RERR IERR ZERR CHI PROB SHARP G-R R-I I-Z PickleDist', file=outFile)
        g = matchDat[:,3].astype(float)
        r = matchDat[:,4].astype(float)
        i = matchDat[:,5].astype(float)
        z = matchDat[:,6].astype(float)
    else:
        print('# F T S Rchunk RA_1 DEC_1 Rmed Rmad RmeanErr Vmed Vmad VmeanErr WScoeff WScoeffp RA_2 DEC_2 U  G  R I Z  UERR GERR RERR IERR  ZERR CHI  PROB SHARP Separation G-R R-I I-Z PickleDist', file=outFile)
        g = matchDat[:,17].astype(float)
        r = matchDat[:,18].astype(float)
        i = matchDat[:,19].astype(float)
        z = matchDat[:,20].astype(float)

    gr = g - r
    ri = r - i
    iz = i - z

    nfMatchDat = matchDat.shape[1]
    meanShift = np.zeros((3))
    for (i, x) in enumerate(gr):
        y = ri[i]
        z = iz[i]
        dist, shiftVec = dist3D([x,y,z], x1, x2)
        meanShift += shiftVec
        for n in range(nfMatchDat):
            print(matchDat[i,n], end=' ', file=outFile) 
        print(gr[i], ri[i], iz[i], dist, file=outFile)

    meanShift /= float(len(gr))
    
    outFile.close()

    return meanShift


if __name__ == "__main__":

    picklesFileName = sys.argv[1]
    matchFileName = sys.argv[2]
    outFileName = sys.argv[3]

    vv, pts = fitPickles(picklesFileName)

    if len(sys.argv)==4:
        meanShift = addDist3D(pts, matchFileName, outFileName)
    else:
        meanShift = addDist3D(pts, matchFileName, outFileName, unMatchedFmt=True)
    

    print(vv)
    print(pts)
    print(meanShift)

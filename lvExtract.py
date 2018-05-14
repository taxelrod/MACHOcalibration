#!/usr/bin/env python
"""
Given an lcstat file, and a threshold, extract and output all stars with variability
below the threshold.  The variability is quantified by Rmad/RmeanErr and similarly for V
"""
import sys
import numpy as np

lcsFileName = sys.argv[1]
varThresh = float(sys.argv[2])

lcsData = np.loadtxt(lcsFileName, dtype=str)

Rmad = lcsData[:,7].astype(float)
RmeanErr = lcsData[:,8].astype(float)
Vmad = lcsData[:,10].astype(float)
VmeanErr = lcsData[:,11].astype(float)

Rvar = Rmad/RmeanErr
Vvar = Vmad/VmeanErr

lowV = np.where((Rvar<varThresh) & (Vvar<varThresh))

print '# F T S Rchunk RA DEC Rmed Rmad RmeanErr Vmed Vmad VmeanErr WScoeff WScoeffp'
nCol = lcsData.shape[1]

for i in lowV[0]:
    for j in range(nCol):
        print lcsData[i,j],' ',
    print ' '

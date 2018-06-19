#!/usr/bin/env python

"""
Load a star file as produced by chunkExtract.py, and calculate in degrees the ra, dec limits
"""

import numpy as np
from astropy import units as u
from astropy.coordinates import Angle
import sys

data = np.loadtxt(sys.argv[1],dtype=str)
nStars = data.shape[0]

raMin = decMin = 1000.0
raMax = decMax = -1000.0

for n in range(nStars):
    ra = Angle(data[n,3] + ' hours')
    radeg = ra.degree

    dec = Angle(data[n,4] + ' degrees')
    decdeg = dec.degree

    raMin = min(radeg, raMin)
    raMax = max(radeg, raMax)
    decMin = min(decdeg, decMin)
    decMax = max(decdeg, decMax)
    
print(raMin, raMax, decMin, decMax)


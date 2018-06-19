#!/usr/bin/env python

import numpy as np
from astropy import units as u
from astropy.coordinates import Angle
import sys

data = np.loadtxt(sys.argv[1],dtype=str)

nflds = data.shape[0]

for n in range(nflds):
    ra = Angle(data[n,1] + ' hours')
    radeg = ra.degree

    dec = Angle(data[n,2] + ' degrees')
    decdeg = dec.degree
    print(data[n,0], radeg, decdeg)


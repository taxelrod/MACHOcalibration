import sys
import numpy as np
import statsmodels.api as sm

def fitPlane(z, zerr, x, y):
    # form x, y, and vector of ones into a matrix
    nPts = len(z)
    if len(x) != nPts or len(y) != nPts:
        sys.exit('fitPlane input vectors must all have same length')
    a = np.column_stack((x, y))
    a = sm.add_constant(a)

    mod_wls = sm.WLS(z, a, weights=1./zerr)
    res_wls = mod_wls.fit()
    print(res_wls.summary())

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

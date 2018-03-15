"""
Toy model for MACHO lc calibration with George/emcee
"""
import numpy as np
import george
from george import kernels
import scipy.optimize as op

import lcScoreBoard

t = 0
r = 0
rerr = 0
rdev = 0
gp = 0

def importLC(lcFileName):
    lcData = np.loadtxt(lcFileName)
    lcDataNew = np.zeros_like(lcData)
    # stupid permutation required - should fix with attached dictionary
    lcDataNew[:,0] = lcData[:,0]
    lcDataNew[:,1] = lcData[:,2]
    lcDataNew[:,2] = lcData[:,3]
    lcDataNew[:,3] = lcData[:,4]
    lcDataNew[:,4] = lcData[:,5]
    lcDataNew[:,5] = lcData[:,1]
    
    lcsb = lcScoreBoard.LcScoreBoard()
    lcsb.addLC(1, lcDataNew)

    return lcsb

def modelLC(lcsb, a, b, id=1):
    global t, r, rerr, rdev
    
    t = lcsb.time
    r = lcsb.rmag
    rerr = lcsb.rerr
    rdev = r - np.median(r)
    kernel = kernels.ExpSquaredKernel(a)
    gp = george.GP(kernel, white_noise=np.log(b*b))
    gp.compute(t, rerr)
    t_pred = np.linspace(np.min(t), np.max(t), 500)
    pred_r, pred_rerr = gp.predict(rdev, t_pred, return_var=True)

    return t, rdev, rerr, t_pred, pred_r, pred_rerr

def nll(p):
    # Update the kernel parameters and compute the likelihood.
    gp.set_parameter_vector(p)
    ll = gp.lnlikelihood(rdev, quiet=True)

    # The scipy optimizer doesn't play well with infinities.
    return -ll if np.isfinite(ll) else 1e25

# And the gradient of the objective function.
def grad_nll(p):
    # Update the kernel parameters and compute the likelihood.
    gp.set_parameter_vector(p)
    return -gp.grad_lnlikelihood(rdev, quiet=True)

def optLC(lcsb, a, b, id=1): 
    global t, r, rerr, rdev, gp

    t = lcsb.time
    r = lcsb.rmag
    rerr = lcsb.rerr
    rdev = r - np.median(r)
#    kernel = kernels.ExpSquaredKernel(a, bounds=(400,40000))
    kernel = kernels.ExpSquaredKernel(a)
    gp = george.GP(kernel, white_noise=np.log(b*b), fit_white_noise=True)
    gp.compute(t, rerr)

    # Print the initial ln-likelihood.
    print(gp.lnlikelihood(rdev))

    # Run the optimization routine.
    p0 = gp.get_parameter_vector()
    results = op.minimize(nll, p0, jac=grad_nll)
    print results.x

    # Update the kernel and print the final log-likelihood.
    gp.set_parameter_vector(results.x)
    print(gp.lnlikelihood(rdev))

    t_pred = np.linspace(np.min(t), np.max(t), 5000)
    pred_r, pred_rerr = gp.predict(rdev, t_pred, return_var=True)

    return t, rdev, rerr, t_pred, pred_r, pred_rerr

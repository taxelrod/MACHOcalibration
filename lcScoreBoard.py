import numpy as np

class LcScoreBoard(object):
    """Keep track of lightcurve data"""

    def __init__(self, debug=False):
        # initialize class members
        self.nPsf = 0  # number of cols
        self.nTime = 0 # number of rows
        self.debug = debug
#        self.time = # 1D array of times, NOT sorted
# remaining arrays are all 2D, [nPsf, nTime] reshaped as needed as lightcurves added
#        self.valid =
#        self.rmag =
#        self.rerr =
#        self.bmag =
#        self.berr =
#        self.obsid =
        self.psfDict = {} # maps psfId to row in self.XX

        if debug:
            self.log = open('Logdbg','w')

    def addLC(self, id, lcData):

        if self.psfDict.has_key(id):
            raise ValueError, 'light curve with id %d already in LcScoreBoard' % id

        # name the columns of the incoming data
#        time = lcData[:,2]
#        rmag = lcData[:,3]
#        rerr = lcData[:,4]
#        bmag = lcData[:,5]
#        berr = lcData[:,6]
#        obsid = lcData[:,7]

        time = lcData[:,0]
        rmag = lcData[:,1]
        rerr = lcData[:,2]
        bmag = lcData[:,3]
        berr = lcData[:,4]
        obsid = lcData[:,5]

        if self.nPsf == 0:
            # we're going to have at least one lightcurve - allocate the class member arrays
            ntPoints = lcData.shape[0]
            self.nTime = ntPoints
            self.validR = np.ones((ntPoints), dtype=bool) # all points in the first LC are valid
            self.validB = np.ones((ntPoints), dtype=bool) # all points in the first LC are valid
            self.time = time.flatten() # remove extraneous dimension from time
            self.obsid = obsid.flatten() # remove extraneous dimension from obsid
            self.rmag = np.zeros((ntPoints), dtype=float)
            self.rmag = rmag
            self.rerr = np.zeros((ntPoints), dtype=float)
            self.rerr = rerr
            self.bmag = np.zeros((ntPoints), dtype=float)
            self.bmag = bmag
            self.berr = np.zeros((ntPoints), dtype=float)
            self.berr = rerr

            self.nPsf = 1
        else:
            #
            # add new row in each self.xx array for this light curve.  Set self.valid=False
            # for the row
            if self.nPsf==1:
                self.validR = np.stack((self.validR, np.zeros((self.nTime), dtype=bool)))
                self.validB = np.stack((self.validB, np.zeros((self.nTime), dtype=bool)))
                self.rmag = np.stack((self.rmag, np.zeros((self.nTime), dtype=float)))
                self.rerr = np.stack((self.rerr, np.zeros((self.nTime), dtype=float)))
                self.bmag = np.stack((self.bmag, np.zeros((self.nTime), dtype=float)))
                self.berr = np.stack((self.berr, np.zeros((self.nTime), dtype=float)))
            else:
                self.validR = np.vstack((self.validR, np.zeros((self.nTime), dtype=bool)))
                self.validB = np.vstack((self.validB, np.zeros((self.nTime), dtype=bool)))
                self.rmag = np.vstack((self.rmag, np.zeros((self.nTime), dtype=float)))
                self.rerr = np.vstack((self.rerr, np.zeros((self.nTime), dtype=float)))
                self.bmag = np.vstack((self.bmag, np.zeros((self.nTime), dtype=float)))
                self.berr = np.vstack((self.berr, np.zeros((self.nTime), dtype=float)))
                                  
            self.nPsf += 1
            
            # add any new times to the end of the scoreboard's time array
            for (it, t) in enumerate(time):
                idTime = np.where(t==self.time)[0]
                if len(idTime) == 0:
                    # add new time to self.time, which means adding new column to self.valid, self.rmag, etc
                    self.time.resize((self.nTime + 1))
                    self.time[self.nTime] = t
                    self.obsid.resize((self.nTime + 1))
                    self.obsid[self.nTime] = obsid[it]
                    self.validR = np.hstack((self.validR, np.zeros((self.nPsf,1), dtype=bool)))
                    self.validB = np.hstack((self.validB, np.zeros((self.nPsf,1), dtype=bool)))
                    self.rmag = np.hstack((self.rmag, np.zeros((self.nPsf,1), dtype=float)))
                    self.rerr = np.hstack((self.rerr, np.zeros((self.nPsf,1), dtype=float)))
                    self.bmag = np.hstack((self.bmag, np.zeros((self.nPsf,1), dtype=float)))
                    self.berr = np.hstack((self.berr, np.zeros((self.nPsf,1), dtype=float)))
                    
                    self.validR[self.nPsf-1, self.nTime] = True
                    self.validB[self.nPsf-1, self.nTime] = True
                    self.rmag[self.nPsf-1, self.nTime] = rmag[it]
                    self.rerr[self.nPsf-1, self.nTime] = rerr[it]
                    self.bmag[self.nPsf-1, self.nTime] = bmag[it]
                    self.berr[self.nPsf-1, self.nTime] = berr[it]
                    self.nTime += 1
                else:
                    # proper time column already exists. Stuff rmag, etc into that column for this row
                    self.validR[self.nPsf-1, idTime] = True
                    self.validB[self.nPsf-1, idTime] = True
                    self.rmag[self.nPsf-1, idTime] = rmag[it]
                    self.rerr[self.nPsf-1, idTime] = rerr[it]
                    self.bmag[self.nPsf-1, idTime] = bmag[it]
                    self.berr[self.nPsf-1, idTime] = berr[it]
 

        self.psfDict[id] = self.nPsf

    def setTemplateObs(self, templateObs):

        templateId = np.where(self.obsid==templateObs)[0]
        if len(templateId) == 0:
            raise ValueError, 'template obs %d not found' % templateObsR
        else:
            templateRmag = self.rmag[:,templateId]  # template R mag for each psf star
            templateBmag = self.bmag[:,templateId]  # template B mag for each psf star

        # process full set of lightcurves, creating self.rdev and self.bdev
        self.rdev = np.zeros((self.nPsf, self.nTime), dtype=float)
        self.bdev = np.zeros((self.nPsf, self.nTime), dtype=float)
        
        for n in range(self.nPsf):
            self.rdev[n,:] = self.rmag[n,:] - templateRmag[n]
            self.bdev[n,:] = self.bmag[n,:] - templateBmag[n]
    
    def extractTime(self, t):
        idTime = np.where(t==self.time)[0]
        if len(idTime) == 0:
            return None, None, None, None, None, None
        else:
            rmag = self.rdev[:,idTime]
            rerr = self.rerr[:,idTime]
            bmag = self.bdev[:,idTime]
            berr = self.berr[:,idTime]
            validR = self.validR[:,idTime]
            validB = self.validB[:,idTime]
            return rmag, rerr, bmag, berr, validR, validB
        
    def calcWsCoeffs(self):
        self.wsCoeffR = np.zeros((self.nPsf, 2), dtype=float)
        self.wsCoeffB = np.zeros((self.nPsf, 2), dtype=float)
        for i in range(self.nPsf):
            idValid = np.where((self.validR[i,:]) & (self.validB[i,:]))[0]
            rmag = self.rdev[i,idValid]
            bmag = self.bdev[i,idValid]
            bMinusr = bmag - rmag
            self.wsCoeffR[i,:] = np.polyfit(bMinusr, rmag, 1)
            self.wsCoeffB[i,:] = np.polyfit(bMinusr, bmag, 1)

    def calcWsShift(self):

        self.wsShiftR = np.zeros((self.nTime),dtype=float)
        self.wsShiftB = np.zeros((self.nTime),dtype=float)
        
        for (i, t) in enumerate(self.time):
            nptsWsShift = 0
            for n in range(self.nPsf):
                if self.validR[n,i] and self.validB[n,i]:
                    self.wsShiftR[i] += np.polyval(self.wsCoeffR[n,:], self.bdev[n, i]-self.rdev[n, i])
                    self.wsShiftB[i] += np.polyval(self.wsCoeffB[n,:], self.bdev[n, i]-self.rdev[n, i])
                    nptsWsShift += 1
            if nptsWsShift > 0:
                    self.wsShiftR[i] /= nptsWsShift
                    self.wsShiftB[i] /= nptsWsShift
            
 
    def filter2pt5Sigma(self):
        """
        Iterate over all times. For each time, calculate weighted stdev for each valid red and blue points.
        Mark points that exceed 2.5 sigma as invalid
        """
        for (i, t) in enumerate(self.time):
            rdev, rerr, bdev, berr, validR, validB = self.extractTime(t)
            ivalidR = np.where(validR)[0]
            ivalidB = np.where(validB)[0]
            rdevV = rdev[ivalidR]
            rerrV = rerr[ivalidR]
            bdevV = bdev[ivalidB]
            berrV = berr[ivalidB]
            
            rwt = 1./(rerrV**2 + 0.01**2)
            rwtvar = np.mean((rdevV - rdevV.mean())**2*rwt)/np.mean(rwt)
            rsigcut = 2.5*np.sqrt(rwtvar)
            idRcut = np.where((validR) & (np.abs(rdev)>rsigcut))[0]
            self.validR[idRcut, i] = False

            bwt = 1./(berrV**2 + 0.01**2)
            bwtvar = np.mean((bdevV - bdevV.mean())**2*bwt)/np.mean(bwt)
            bsigcut = 2.5*np.sqrt(bwtvar)
            idBcut = np.where((validB) & (np.abs(bdev)>bsigcut))[0]
            self.validB[idBcut, i] = False
            if self.debug:
                print >>self.log, t, rsigcut, bsigcut, validR, validB, idRcut, idBcut

        if self.debug:
            self.log.flush()

    def filterDDB(self):

        """
        Iterate over all times. For each time, calculate weighted stdev for each valid red and blue points.
        Mark points that exceed the DDB quantity 'dfmagdifmn' in magnorm.F as invalid
        """
        for (i, t) in enumerate(self.time):
            rdev, rerr, bdev, berr, validR, validB = self.extractTime(t)
            ivalidR = np.where(validR)[0]
            ivalidB = np.where(validB)[0]
            rdevV = rdev[ivalidR]
            rerrV = rerr[ivalidR]
            bdevV = bdev[ivalidB]
            berrV = berr[ivalidB]
            
            rwt = 1./(rerrV**2 + 0.01**2)
            rwtvar = np.mean((rdevV - rdevV.mean())**2*rwt)/np.mean(rwt)
            rabsnormcut = np.maximum(np.sqrt(rwtvar)*rerr, 0.05)
            idRcut = np.where((validR) & (np.abs(rdev)>rabsnormcut))[0]
            self.validR[idRcut, i] = False

            bwt = 1./(berrV**2 + 0.01**2)
            bwtvar = np.mean((bdevV - bdevV.mean())**2*bwt)/np.mean(bwt)
            babsnormcut = np.maximum(np.sqrt(bwtvar)*berr, 0.05)
            idBcut = np.where((validB) & (np.abs(bdev)>babsnormcut))[0]
            self.validB[idBcut, i] = False
            if self.debug:
                print >>self.log, 'DDB: ',t, rabsnormcut, babsnormcut, validR, validB, idRcut, idBcut

        if self.debug:
            self.log.flush()

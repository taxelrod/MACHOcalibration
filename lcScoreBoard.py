import numpy as np

class LcScoreBoard(object):
    """Keep track of lightcurve data"""
    def __init__(self):
        # initialize class members
        self.nPsf = 0  # number of cols
        self.nTime = 0 # number of rows
#        self.time = # 1D array of times, NOT sorted
# remaining arrays are all 2D, [nPsf, nTime] reshaped as needed as lightcurves added
#        self.valid =
#        self.rmag =
#        self.rerr =
#        self.bmag =
#        self.berr =
#        self.obsid =
        self.psfDict = {} # maps psfId to row in self.XX
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

        if self.nPsf == 0:
            # we're going to have at least one lightcurve - allocate the class member arrays
            ntPoints = lcData.shape[0]
            self.nTime = ntPoints
            self.valid = np.ones((ntPoints), dtype=bool) # all points in the first LC are valid
            self.time = time.flatten() # remove extraneous dimension from time
            self.rmag = np.zeros((ntPoints), dtype=float)
            self.rmag = rmag
            # etc
            self.nPsf = 1
        else:
            #
            # add new row in each self.xx array for this light curve.  Set self.valid=False
            # for the row
            if self.nPsf==1:
                self.valid = np.stack((self.valid, np.zeros((self.nTime), dtype=bool)))
                self.rmag = np.stack((self.rmag, np.zeros((self.nTime), dtype=float)))
            else:
                self.valid = np.vstack((self.valid, np.zeros((self.nTime), dtype=bool)))
                self.rmag = np.vstack((self.rmag, np.zeros((self.nTime), dtype=float)))
                                   
            self.nPsf += 1
            
            # etc
            
            # add any new times to the end of the scoreboard's time array
            for (it, t) in enumerate(time):
                idTime = np.where(t==self.time)[0]
                if len(idTime) == 0:
                    # add new time to self.time, which means adding new column to self.valid, self.rmag, etc
                    self.time.resize((self.nTime + 1))
                    self.time[self.nTime] = t
                    self.valid = np.hstack((self.valid, np.zeros((self.nPsf,1), dtype=bool)))
                    self.rmag = np.hstack((self.rmag, np.zeros((self.nPsf,1), dtype=float)))
                    # etc
                    self.valid[self.nPsf-1, self.nTime] = True
                    self.rmag[self.nPsf-1, self.nTime] = rmag[it]
                    print >>self.log, 'rmag1 %d %d %f' % (self.nPsf-1, self.nTime, rmag[it])
                    self.nTime += 1
                else:
                    # proper time column already exists. Stuff rmag, etc into that column for this row
                    self.valid[self.nPsf-1, idTime] = True
                    self.rmag[self.nPsf-1, idTime] = rmag[it]
                    print >>self.log, 'rmag2 %d %d %f' % (self.nPsf-1, idTime, rmag[it])
                    # etc

        self.psfDict[id] = self.nPsf
        self.log.flush()

    def extractTime(self, t):
        idTime = np.where(t==self.time)[0]
        if len(idTime) == 0:
            return None
        else:
            rmag = self.rmag[:,idTime]
            idValid = np.where(self.valid[:,idTime])[0]
            if len(idValid)==0:
                return None
            else:
                return rmag[idValid]
        
    def calcWsCoeffs(self):
        pass
    def filter25Sigma(self):
        pass
    def filterDDB(self):
        pass

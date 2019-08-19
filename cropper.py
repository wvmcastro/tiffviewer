import numpy as np

class Croper():

    def __init__(self, blocksx, blocksy):
        self._blocksx = blocksx
        self._blocksy = blocksy

        self.gridCornersX = []
        self.gridCornersY = []

    def sortCorners(self):
        x = np.argsort(self.gridCornersX)
        
        xcorners = self.gridCornersX
        ycorners = self.gridCornersY
        
        self.gridCornersX = []
        self.gridCornersY = []

        if ycorners[x[0]] < ycorners[x[1]]:
            self.gridCornersX += [xcorners[x[0]], xcorners[x[1]]]
            self.gridCornersY += [ycorners[x[0]], ycorners[x[1]]]
        else:
            self.gridCornersX += [xcorners[x[1]], xcorners[x[0]]]
            self.gridCornersY += [ycorners[x[1]], ycorners[x[0]]]
        
        if ycorners[x[2]] < ycorners[x[3]]:
            self.gridCornersX += [xcorners[x[3]], xcorners[x[2]]]
            self.gridCornersY += [ycorners[x[3]], ycorners[x[2]]]
        else:
            self.gridCornersX += [xcorners[x[2]], xcorners[x[3]]]
            self.gridCornersY += [ycorners[x[2]], ycorners[x[3]]]
    
    def calcgridLines(self):
        corners = np.array([(x,y) for x,y in zip(self.gridCornersX, self.gridCornersY)])
        xbvec = corners[-1, ...] - corners[0, ...]
        xtvec = corners[2, ...] - corners[0, ...]
        
        xbvec_norm = np.linalg.norm(xbvec)
        xtvec_norm = np.linalg.norm(xtvec)

        b = xbvec_norm / self._blocksx
        t = xtvec_norm / self._blocksx

        xbvec /= xbvec_norm
        xtvec /= xtvec_norm

        
        # for i in range(1, self._blocksx)


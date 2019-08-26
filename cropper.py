import numpy as np

class Cropper():

    def __init__(self, blocksx, blocksy):
        self._blocksx = blocksx
        self._blocksy = blocksy

        self.gridCornersX = []
        self.gridCornersY = []
        self._grid = np.zeros((blocksy+1, blocksx+1, 2))

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
    
    def calcgridLines(self) -> np.ndarray:
        #     xt
        #     __ 
        # yl /  \  yr
        #   /____\ 
        #     xb

        xs = self.gridCornersX
        ys = self.gridCornersY
        
        origin = np.array([xs[0], ys[0]])
        north = np.array([xs[1], ys[1]])
        north_east = np.array([xs[2], ys[2]])
        east = np.array([xs[3], ys[3]])


        yl_vec = origin - north
        yr_vec = east - north_east

        for i in range(self._blocksy+1):
            alpha = i / self._blocksy
            o = north + (alpha * yl_vec)
            e = north_east + (alpha * yr_vec)
            x_vec = e - o
            
            for j in range(self._blocksx+1):
                betha = j / self._blocksx
                point = o + (betha * x_vec)
                self._grid[i, j, ...] = point
        
        return self._grid


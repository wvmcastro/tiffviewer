from typing import Tuple
import numpy as np
import math
import cv2
import copy
from time import sleep
import make_numbers_raiz_b5
import make_numbers_sede_p4
import make_numbers_triangulo_b7
import make_numbers_triangulo_p7
import make_numbers_sede_p1

class Cropper():

    def __init__(self, blocks:int, 
                       parcelsx:int, 
                       parcelsy:int, 
                       cornerPoints: np.ndarray = None) -> None:
        self._blocks = blocks
        self._parcelsx = parcelsx
        self._parcelsy = parcelsy
        
        # X coordinates of the corners of the blocks, list of lists: every list is a list of 4 corners
        self.gridCornersX = []
        # Y coordinates of the corners of the blocks, list of lists: every list is a list of 4 corners
        self.gridCornersY = []
        # set of all the points of the grid, list of lists: every list is a block (grid)
        self._grids = []

        self._w = self._h = 0

        if cornerPoints is not None:
            self.loadCornerPoints(cornerPoints)
    
    def loadCornerPoints(self, cornerPoints: np.ndarray) -> None:
        self.gridCornersX = [x for x in cornerPoints[..., 1]]
        self.gridCornersY = [y for y in cornerPoints[..., 0]]

    def sortCorners(self):
        n = 4*self._blocks
        gridCornersX = []
        gridCornersY = []

        for i in range(0, n, 4):
            y = np.argsort(self.gridCornersY[i:i+4])

            xcorners = copy.copy(self.gridCornersX[i:i+4])
            ycorners = copy.copy(self.gridCornersY[i:i+4])

            tl = np.array([xcorners[y[0]], ycorners[y[0]]])
            corners = np.array([xcorners, ycorners]).T

            v1 = corners[y[1], ...] - tl
            v2 = corners[y[2], ...] - tl

            ang1 = math.atan(v1[1] / v1[0])
            ang2 = math.atan(v2[1] / v2[0])

            if abs(ang1) < abs(ang2):
                tr = corners[y[1], ...]
                bl = corners[y[2], ...]
            else:
                tr = corners[y[2], ...]
                bl = corners[y[1], ...]
            
            br = corners[y[3], ...]
        
            gridCornersX.append([tl[0], tr[0], br[0], bl[0]])
            gridCornersY.append([tl[1], tr[1], br[1], bl[1]])
        
        self.gridCornersX = gridCornersX
        self.gridCornersY = gridCornersY
    
    def calcGridsPoints(self) -> np.ndarray:

        # for every block...
        for gridCornersX, gridCornersY in \
            zip(self.gridCornersX, self.gridCornersY):

            dst = np.array([gridCornersX, gridCornersY], dtype="float32")
            dst = dst.T
            # calculating the rectangles from the trapeziums through the transform function
            src = self.getDstTransformPoints(dst)

            # Base transform matrix that links rectangles to their respective trapeziums
            M = cv2.getPerspectiveTransform(src, dst)

            # src[1,0] is width of the resulting rectangle (block)
            x_len = src[1,0] / self._parcelsx
            # src[3,1] is height of the resulting rectangle (block)
            y_len = src[3,1] / self._parcelsy

            grid = np.zeros((self._parcelsy+1, self._parcelsx+1, 2))
            for y in range(self._parcelsy+1):
                for x in range(self._parcelsx+1):
                    # through the known points of the transformed rectangle, calculates the points in the corresponding rectangle using the M matrix
                    point = M @ np.array([x*x_len, y*y_len, 1], dtype="float32")
                    # divides by homogeneous coordinate to get the real coordinates
                    grid[y, x] = point[:2] / point[2]
            
            self._grids.append(grid)
        return self._grids
    
    def getDstTransformPoints(self, srcPoints) -> np.ndarray:
        w1 = np.linalg.norm(srcPoints[1, ...] - srcPoints[0, ...])
        w2 = np.linalg.norm(srcPoints[3, ...] - srcPoints[2, ...])
        w = max(w1, w2)

        h1 = np.linalg.norm(srcPoints[3, ...] - srcPoints[0, ...])
        h2 = np.linalg.norm(srcPoints[2, ...] - srcPoints[1, ...])
        h = max(h1, h2)

        tl = np.array([0, 0])
        tr = np.array([w, 0])
        br = np.array([w, h])
        bl = np.array([0, h])

        return np.array([tl, tr, br, bl], dtype="float32")
    
    def getCrop(self, img: np.ndarray, 
                    srcPoints: np.ndarray, 
                    dstPoints: np.ndarray) -> np.ndarray:
        if not (self._w and self._h):
            self._w, self._h = int(srcPoints[2, 0]), int(srcPoints[2, 1])
        crop = np.zeros((self._h, self._w, 3))

        M = cv2.getPerspectiveTransform(srcPoints, dstPoints)
        for y in range(self._h):
            for x in range(self._w):
                imgPoint = M @ np.array([x, y, 1])
                j, i = imgPoint[:2] / imgPoint[2]
                crop[y, x] = np.flip(img[int(i), int(j)])
        
        return crop
    
    def saveCropsP2(self, img: np.ndarray, 
                          outputdir: str = "",
                          timestamp: str = "", 
                          scale: float = 1) -> None:
        s = scale
        for k, g in enumerate(self._grids):
            for i in range(self._parcelsy):
                for j in range(self._parcelsx):
                    # scales every point of the block
                    dst = np.array([s*g[i,j], s*g[i, j+1],  s*g[i+1, j+1], s*g[i+1, j]],
                                   dtype="float32")
                    # gets the corresponding rectangle of the (scaled) trapezium
                    src = self.getDstTransformPoints(dst)
                    # given the coordinates, extracts the crop of the parcel from the original image
                    crop = self.getCrop(img, src, dst)
                    # to run local tests, replace self.make_numbers_p2 by the function you implemented for your experiment
                    block, number = self.make_numbers_p2(i, j, self._parcelsy, self._parcelsx, k+1)
                    name = outputdir + timestamp + "-" + "%02d" % (block) + "-" + "%03d" % (number) + ".png"
                    cv2.imwrite(name, crop)
    
    # this is the implementation to track the zigzag numbers of the parcels in the P2 sketch, check the sketch to understand this better
    def make_numbers_p2(self, line, col, numLines, numColumns, p2Block: int):
        if col % 2 == 0:
            oy = numLines - 1
        else:
            oy = 0

        if p2Block == 1:
            start_number = 1
        elif p2Block == 2:
            start_number = 111
        else:
            start_number = 221
        
        index = col * numLines + abs(line - oy)
        index += start_number
        return p2Block, index
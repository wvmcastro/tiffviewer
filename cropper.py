from typing import Tuple
import numpy as np
import math
import cv2
import copy
from time import sleep

class Cropper():

    def __init__(self, blocks:int, 
                       parcelsx:int, 
                       parcelsy:int, 
                       cornerPoints: np.ndarray = None) -> None:
        self._blocks = blocks
        self._parcelsx = parcelsx
        self._parcelsy = parcelsy

        self.gridCornersX = []
        self.gridCornersY = []
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

        for gridCornersX, gridCornersY in \
            zip(self.gridCornersX, self.gridCornersY):

            dst = np.array([gridCornersX, gridCornersY], dtype="float32")
            dst = dst.T
            src = self.getDstTransformPoints(dst)

            M = cv2.getPerspectiveTransform(src, dst)

            x_len = src[1,0] / self._parcelsx
            y_len = src[3,1] / self._parcelsy

            grid = np.zeros((self._parcelsy+1, self._parcelsx+1, 2))
            for y in range(self._parcelsy+1):
                for x in range(self._parcelsx+1):
                    point = M @ np.array([x*x_len, y*y_len, 1], dtype="float32")
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
        

    def saveCropsP4(self, img: np.ndarray, 
                          outputdir: str = "",
                          timestamp: str = "", 
                          scale: float = 1) -> None:
        s = scale
        for k, g in enumerate(self._grids):
            for i in range(self._parcelsy):
                for j in range(self._parcelsx):
                    dst = np.array([s*g[i,j], s*g[i, j+1],  s*g[i+1, j+1], s*g[i+1, j]],
                                   dtype="float32")
                    src = self.getDstTransformPoints(dst)
                    crop = self.getCrop(img, src, dst)
                    block, number = self.make_numbers_p4((8*k)+i, j, self._parcelsy, 4)
                    name = outputdir + timestamp + "-" + "%02d" % (block) + "-" + "%02d" % (number) + ".png"
                    cv2.imwrite(name, crop)
    
    def make_numbers_p4(self, line, column, l, c) -> Tuple[int, int]:
        blocks = np.array([[64, 65, 66, 67, 68, 69, 70],
                        [63, 62, 61, 60, 59, 58, 57],
                        [50, 51, 52, 53, 54, 55, 56],
                        [49, 48, 47, 46, 45, 44, 43],
                        [36, 37, 38, 39, 40, 41, 42],
                        [35, 34, 33, 32, 31, 30, 29],
                        [22, 23, 24, 25, 26, 27, 28],
                        [21, 20, 19, 18, 17, 16, 15],
                        [8, 9, 10, 11, 12, 13, 14],
                        [7, 6, 5, 4, 3, 2, 1]])

        block1 = np.array([[8, 9, 24, 25],
                        [7, 10, 23, 26],
                        [6, 11, 22, 27],
                        [5, 12, 21, 28],
                        [4, 13, 20, 29],
                        [3, 14, 18, 31],
                        [2, 15, 16, 30],
                        [1, 16, 17, 32]])
        block2 = np.flip(block1, axis=1)

        a = line // l
        blockNumber = blocks[a, column // c]
        block = block1 if a % 2 == 0 else block2
        return blockNumber, block[line % l, column % c]
    
    def saveCropsP2(self, img: np.ndarray, 
                          outputdir: str = "",
                          timestamp: str = "", 
                          scale: float = 1) -> None:
        s = scale
        for k, g in enumerate(self._grids):
            for i in range(self._parcelsy):
                for j in range(self._parcelsx):
                    dst = np.array([s*g[i,j], s*g[i, j+1],  s*g[i+1, j+1], s*g[i+1, j]],
                                   dtype="float32")
                    src = self.getDstTransformPoints(dst)
                    crop = self.getCrop(img, src, dst)
                    block, number = self.make_numbers_p2(i, j, self._parcelsy, self._parcelsx, k+1)
                    name = outputdir + timestamp + "-" + "%02d" % (block) + "-" + "%03d" % (number) + ".png"
                    cv2.imwrite(name, crop)
    
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
        
        
        
        
        


from typing import Iterable
import matplotlib.pyplot as plt
import numpy as np

class GUI():
    def __init__(self, figure, cornersx, cornersy):
        self.gridCornersX = cornersx
        self.gridCornersY = cornersy
        self._figure = figure
        self._cid = self._figure.canvas.mpl_connect("button_press_event", self._onClick)
        self._axes = self._addSubplot()

        plt.draw()

    def _addSubplot(self) -> None:
        ax = self._figure.add_subplot(111)
        return ax
        
    def _onClick(self, event) -> None:
        
        if event.inaxes != self._axes:
            return
        
        x, y = event.xdata, event.ydata
        self.gridCornersX.append(x)
        self.gridCornersY.append(y)

        self._axes.plot(x, y, 'ro')
        plt.draw()

        if len(self.gridCornersX) == 4:
            self._figure.canvas.mpl_disconnect(self._cid)
            # self._drawGrid()
    
    def drawRectangle(self, xcorners: Iterable, ycorners: Iterable):
        plt.plot(xcorners, ycorners, 'g')
        plt.plot([xcorners[-1], xcorners[0]], 
                 [ycorners[-1], ycorners[0]], 'g')

        plt.draw()

    def pause(self):
        plt.pause(0.016)

    def block(self):
        plt.show()

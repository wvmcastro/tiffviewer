from argparse import ArgumentParser
import matplotlib.pyplot as plt
import rasterio
from time import sleep

from gui import GUI
from cropper import Cropper

def makeParser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("grid_x", type=int, help="number blocks x axis")
    parser.add_argument("grid_y", type=int, help="number blocks y axis")

    return parser

if __name__ == "__main__":
    parser = makeParser()
    args = parser.parse_args()
    
    cropper = Cropper(args.grid_x, args.grid_y)
    gui = GUI(plt.figure(), cropper.gridCornersX, cropper.gridCornersY)
    
    while len(cropper.gridCornersX) != 4:
        gui.pause()
    
    cropper.sortCorners()
    gui.drawRectangle(cropper.gridCornersX, cropper.gridCornersY)
    points = cropper.calcgridLines()
    gui.drawPoints(points[..., 0], points[..., 1])
    gui.drawGridLines(points)


    gui.block()
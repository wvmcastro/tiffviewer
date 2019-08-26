import numpy as np
from argparse import ArgumentParser
import rasterio
from rasterio.enums import Resampling
import matplotlib.pyplot as plt

from gui import GUI
from cropper import Cropper

def makeParser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("img", type=str, help="Image path")
    parser.add_argument("--grid_x", type=int, default=1, help="number blocks x axis")
    parser.add_argument("--grid_y", type=int, default=1, help="number blocks y axis")

    return parser

def calc_overviews(dataset) -> None:
    have_overviews = True
    for i in dataset.indexes:
        have_overviews &= dataset.overviews(i) != []
    
    if not have_overviews:
        print("Calculating Overviews")
        factors = [1, 4, 8, 16]
        dataset.build_overviews(factors, Resampling.average)
        dataset.update_tags(ns="rio_overview", resampling="average")

if __name__ == '__main__':
    parser = makeParser()
    args = parser.parse_args()
    
    with rasterio.open(args.img, 'r+') as dataset:
        print("Loading image")
        print("(w, h): %r, %r" % (dataset.width, dataset.height))
        print("Number of bands: %r" %(dataset.count))
        calc_overviews(dataset)
        r, g, b = dataset.read([1,2,3], out_shape=(dataset.height // 4, dataset.width // 4))
        rgb = np.dstack((r, g, b))
        print("Image loaded")
    
    
    # image = plt.imshow(rgb)
    cropper = Cropper(args.grid_x, args.grid_y)
    gui = GUI(plt.figure(), cropper.gridCornersX, cropper.gridCornersY)
    gui.imshow(rgb)

    while len(cropper.gridCornersX) != 4:
       gui.pause()
    
    cropper.sortCorners()
    gui.drawRectangle(cropper.gridCornersX, cropper.gridCornersY)
    points = cropper.calcgridLines()
    gui.drawPoints(points[..., 0], points[..., 1])
    gui.drawGridLines(points, color='r')


    gui.block()
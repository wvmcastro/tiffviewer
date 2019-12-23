from typing import List
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
    parser.add_argument("--blocks", type=int, default=1, help="number of blocks")
    parser.add_argument("--grid_x", type=int, default=1, help="number  of \
                        parcels inside each block in x axis")
    parser.add_argument("--grid_y", type=int, default=1, help="number  of \
                        parcels inside each block in y axis")
    parser.add_argument("--points", type=str, help="file with the 4 points of the block")
    parser.add_argument("--save_points", action="store_true")
    parser.add_argument("--timestamp", type=str, default="0000-00-00")
    parser.add_argument("--output_dir", type=str, default="", help="output directory\
                            where files should be saved")

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

def save_points(tifFilename: str, points: np.ndarray) -> None:
    pointsFilename = tifFilename.split('.')[0] + ".npy"
    np.save(pointsFilename, points)

def flat_list(l: List) -> List:
    fl = []
    for subList in l:
        fl += subList
    return fl


if __name__ == '__main__':
    """ TODO:
                - Criar arquivos para imagens temporárias 
                - Ajustar a grid iterativamente"""
    parser = makeParser()
    args = parser.parse_args()
    
    with rasterio.open(args.img, 'r+') as dataset:
        print("Loading image")
        print("(w, h): %r, %r" % (dataset.width, dataset.height))
        print("Number of bands: %r" %(dataset.count))
        print("Transform:")
        print(dataset.transform)
        calc_overviews(dataset)
        ro, go, bo = dataset.read([1,2,3], out_shape=(3, dataset.height, dataset.width))
        rd, gd, bd = dataset.read([1,2,3], out_shape=(3, dataset.height // 4, dataset.width // 4))
        rgb = np.dstack((rd, gd, bd))
        print("Image loaded")
    
    
    if args.points is not None:
        mycropper = Cropper(args.blocks, args.grid_x, args.grid_y, np.load(args.points))
    else:
        mycropper = Cropper(args.blocks, args.grid_x, args.grid_y)
    
    
    gui = GUI(plt.figure(), mycropper.gridCornersX, 
              mycropper.gridCornersY, npoints=4*args.blocks)
    gui.imshow(rgb)
    while len(mycropper.gridCornersX) < 4 * args.blocks:
       gui.pause()
    
    mycropper.sortCorners()
    # gui.drawRectangle(mycropper.gridCornersX, mycropper.gridCornersY)
    grids = mycropper.calcGridsPoints()
    for points in grids:
        gui.drawPoints(points[..., 0], points[..., 1])
    
    gui.drawGridsLines(grids, color='r')

    if args.output_dir != "":
        mycropper.saveCropsP2(np.dstack((ro, go, bo)), 
                            outputdir=args.output_dir,
                            timestamp=args.timestamp,
                            scale=4)
        
    gui.block()

    if args.save_points == True:
        corners = np.array([flat_list(mycropper.gridCornersY), 
                            flat_list(mycropper.gridCornersX)]).T
        save_points(args.img, corners)

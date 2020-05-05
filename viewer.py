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
    parser.add_argument("img", type=str, help="Image path (.tif file)")
    parser.add_argument("--blocks", type=int, default=1, help="number of blocks (sets of several parcels, \
        every block has to have the same amount of parcels)")
    parser.add_argument("--grid_x", type=int, default=1, help="number  of \
                        parcels inside each block in x axis")
    parser.add_argument("--grid_y", type=int, default=1, help="number  of \
                        parcels inside each block in y axis")
    parser.add_argument("--points", type=str, help="file with the 4 points of the block, used to avoid using the GUI everytime")
    parser.add_argument("--save_points", help="saves the user's drawn points in a file named <tif_file_name>.npy", action="store_true")
    parser.add_argument("--timestamp", help="timestamp used to name the generated images' names", type=str, default="0000-00-00")
    # the filenames are going to be: YYYY-MM-DD-BLOCKID-PARCELID
    parser.add_argument("--output_dir", type=str, default="", help="output directory\
                            where files should be saved")

    return parser

def calc_overviews(dataset) -> None:
    have_overviews = True
    for i in dataset.indexes:
        have_overviews &= dataset.overviews(i) != []
    
    if not have_overviews:
        print("Calculating Overviews")
        # hard-coded zoom levels in the ortomosaic
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
        # o: original
        # d: redimensioned (1/4 of original img size)
        ro, go, bo = dataset.read([1,2,3], out_shape=(3, dataset.height, dataset.width))
        rd, gd, bd = dataset.read([1,2,3], out_shape=(3, dataset.height // 4, dataset.width // 4))
        # rgb representation of the img
        rgb = np.dstack((rd, gd, bd))
        print("Image loaded")
    
    
    if args.points is not None:
        # pre-loaded points
        mycropper = Cropper(args.blocks, args.grid_x, args.grid_y, np.load(args.points))
    else:
        # user has to draw the points
        mycropper = Cropper(args.blocks, args.grid_x, args.grid_y)
    
    
    gui = GUI(plt.figure(), mycropper.gridCornersX, 
              mycropper.gridCornersY, npoints=4*args.blocks)
    gui.imshow(rgb)
    while len(mycropper.gridCornersX) < 4 * args.blocks:
       gui.pause()
    
    mycropper.sortCorners()
    gui.drawRectangle(mycropper.gridCornersX, mycropper.gridCornersY)
    grids = mycropper.calcGridsPoints()
    for points in grids:
        gui.drawPoints(points[..., 0], points[..., 1])
    
    gui.drawGridsLines(grids, color='r')

    # tip: comment the if below if you only want to view if your drawing of the blocks was good enough to generate decent parcels
    if args.output_dir != "":
        # scale must be the same rate of the redimension of rd, gd, bd
        # the function used below will be changed for the corresponding experiment that you implement
        # TODO: turn this into a parsed argument
        mycropper.saveCropsP2(np.dstack((ro, go, bo)), 
                            outputdir=args.output_dir,
                            timestamp=args.timestamp,
                            scale=4)
        
    gui.block()

    if args.save_points == True:
        corners = np.array([flat_list(mycropper.gridCornersY), 
                            flat_list(mycropper.gridCornersX)]).T
        save_points(args.img, corners)

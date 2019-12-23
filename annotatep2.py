from typing import Tuple, List
from argparse import ArgumentParser
from PIL import Image
import json
import math
import os

import torch
from torchvision import transforms

""" 
    author: Wellington Castro
    date: 12/11/2019

    This script is just a helper to match the image crops from 
    Embrapa's plantation  with the values measured by its specialists
    in the corresponding csv file. This was particularly useful in the
    Sede P2 platation.
"""

def load_csv(path: str) -> Tuple:
    values = []

    with open(path, 'r') as csv:
        for line in csv:
            cells = line.split(',')
            v = (int(cells[1]), int(cells[-1]))
            # if cells[0] == "P2":
            values.append(v)

    return tuple(values)

def ystatics(values):
    s = 0
    n = 0
    std = 0

    min_ = math.inf
    max_ = -math.inf

    for v in values:
        min_ = min(v, min_)
        max_ = max(v, max_)
        n += 1
        s += v
    
    mean = s / n

    for v in values:
        std += (v - mean)**2
    
    std = math.sqrt(std/n)
    return mean, std, min_, max_

def xstatics(root: str, files: List[str]):
    n = 1
    toTensor = transforms.ToTensor()
    s = toTensor(Image.open(root + files[0]))

    for f in files[:1]:
        s += toTensor(Image.open(root + f))
        n += 1
    
    mean = s / n
    
    std = (mean - toTensor(Image.open(root + files[0])))**2 / n
    for f in files[1:]:
        std += (mean - toTensor(Image.open(root + f)))**2 / n
    
    std = torch.sqrt(std)
    num_pixels = std.shape[1] * std.shape[2]
    
    mean = torch.tensor([mean[0, ...].sum(), 
                         mean[1, ...].sum(), 
                         mean[2, ...].sum()]) / num_pixels
    
    std = torch.tensor([std[0, ...].sum(), 
                        std[1, ...].sum(), 
                        std[2, ...].sum()]) / num_pixels
    
    return mean, std
    


def annotate(dataset_path: str, values: List):
    dataset = dict()
    dataset["data"] = dict()
    for root, _, files in os.walk(dataset_path):
        if files != []:
            files = sorted(files)
            xmean, xstd = xstatics(root, files)
            for i, f in enumerate(files):
                print(f, i)
                dataset["data"][f] = values[i][1]
    
    ymean, ystd, ymin, ymax = ystatics(tuple(v[1] for v in values))
    
    dataset["statistics"] = dict()
    dataset["statistics"]["y"] = dict()
    dataset["statistics"]["y"]["mean"] = ymean
    dataset["statistics"]["y"]["std"] = ystd
    dataset["statistics"]["y"]["min"] = ymin
    dataset["statistics"]["y"]["max"] = ymax

    dataset["statistics"]["x"] = dict()
    dataset["statistics"]["x"]["mean"] = [mean.item() for mean in xmean ]
    dataset["statistics"]["x"]["std"] = [std.item() for std in xstd]
    return dataset


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("folder", type=str)
    parser.add_argument("csv", type=str)
    args = parser.parse_args()

    values = load_csv(args.csv)
    annotations = annotate(args.folder, values)

    filename = args.folder + "labels/annotation.json"
    with open(filename, "w+") as fp:
        json.dump(annotations, fp)
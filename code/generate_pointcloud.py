import cv2 as cv
import numpy as np

IMG_PATH = "data/images/00001.png"
DEPTH_PATH = "data/depth/00001.npy"

img = cv.imread(IMG_PATH)
#print(img.shape)
depth = np.load(DEPTH_PATH)
#print(depth.shape)

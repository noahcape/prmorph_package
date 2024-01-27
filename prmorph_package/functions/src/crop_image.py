import math
import statistics
from typing import List, Tuple
import cv2 as cv
import numpy as np


Point = Tuple[int, int]
Pixels = List[Point]

def rotate_upright(img, pct = 0.10):
    if len(img[0]) < len(img):
        img = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)
        
    x = len(img[0])
    y = len(img)
    delta_x = math.floor(x*pct)
    delta_y = math.floor(y*pct)

    cropped_img = img[delta_y:y-delta_y, delta_x:x-delta_x]
    cropped_equ = cv.equalizeHist(cropped_img)


    cropped_equ[cropped_equ < 225] = 0

    vec = [0] * len(cropped_equ)

    for (index, row) in enumerate(cropped_equ):
        vec[index] = sum(row != 0)

    # if left_med > right_med then in correct orientation
    # else flip 180 degrees
    left_med = statistics.median(vec[50:150])
    right_med = statistics.median(vec[-150:-50])
    if right_med > left_med:
        img = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)
        img = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)

    return img

def locate_fish_bounds(img):
    img = np.array(img).T

    nose = None
    tail = None

    for i in range(len(img)):
        dark_pixels = np.array(np.where(img[i] < 130)).size

        if not nose and dark_pixels > 10:
            nose = i

        if nose and dark_pixels == 0:
            tail = i
            return (nose, tail)



def from_bottom(img):
    bottom = None
    top = None 
    num_dark = 0

    for i in range(len(img) - 1, -1, -1):
        b_values = img[i]

        dark_pixels = np.array(np.where(b_values < 130)).size

        if dark_pixels > 100:
            num_dark += 1

        if num_dark > 500 and dark_pixels < 50 and not bottom:
            bottom = i
            num_dark = 0

        if num_dark > 100 and dark_pixels < 200 and bottom and not top:
            top = i
            return (top, bottom)


def adjust_top(img, top):
    num_dark = 0

    for i in range(top, top + 100):
        b_values = img[i]

        dark_pixels = np.array(np.where(b_values < 130)).size

        if dark_pixels > 100:
            num_dark += 1

    return -100 if num_dark > 50 else 100


'''
Main method used to get the placement of the fish.
'''


def main(img_path, flip):
    image = cv.imread(img_path, 0)

    # rotate image if needed
    image = rotate_upright(image)

    # clahe = cv.createCLAHE(clipLimit=1, tileGridSize=(8, 8))
    clahe = cv.createCLAHE(clipLimit=0.5, tileGridSize=(8, 8))
    image_clahe = clahe.apply(image)

    (top, bottom) = from_bottom(image_clahe)    
    top += adjust_top(image_clahe, top)
    new_image = image_clahe[top:bottom,:]
    (nose, tail) = locate_fish_bounds(new_image)

    return (top, bottom, nose - 25, tail + 30)
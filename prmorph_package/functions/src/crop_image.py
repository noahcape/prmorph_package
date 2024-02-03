import math
import statistics
from typing import List, Tuple
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt


Point = Tuple[int, int]
Pixels = List[Point]

def crop_top(img, pct):
    y = len(img)
    delta_y = math.floor(y*pct)

    return img[delta_y:y, 0:len(img[0])]

def crop_bottom(img, pct):
    y = len(img)
    delta_y = math.floor(y*pct)

    return (img[0:y-delta_y, 0:len(img[0])], delta_y)

def slope_left(vec):
    slope = vec[500] - vec[0]
    return slope / 500

def slope_right(vec):
    slope = vec[-100] - vec[-1]
    return slope / 100

def crop_dark_img(img, pct = 0.1):
    bottom = len(img)

    clahe = cv.createCLAHE(clipLimit=0.5, tileGridSize=(8, 8))

    img_equ = clahe.apply(img)

    # img_equ = cv.equalizeHist(img)
    # img_equ[img_equ < 250] = 0

    vec = [0] * len(img_equ)

    for (index, row) in enumerate(img_equ):
        vec[index] = sum(row > 150)

    # first stretch of zero after high peak
    # wait fro another peak over 100 next stretch of zero 
    # stretch is greater than 100 

    count_down_first = 100
    count_down_second = 100
    first_stretch = -1
    second_stretch = -1

    for (index, num_dark) in enumerate(vec):
        # start looking for first stretch
        if num_dark > 100 and first_stretch == -1:
            first_stretch = -2

        # in first stretch
        if first_stretch == -2 and num_dark == 0:
            count_down_first -= 1

        # set first stretch
        if count_down_first <= 0 and first_stretch == -2:
            first_stretch = index

        # start looking for second
        if num_dark > 100 and second_stretch == -1 and count_down_first <= 0:
            second_stretch = -2
            
        # start counting second stretch
        if num_dark == 0 and second_stretch == -2:
            count_down_second -= 1

        # found second
        if count_down_second <= 0:
            second_stretch = index
            break

    # plt.imshow(img_equ)
    # plt.show()
    # plt.plot(np.arange(len(img)), vec)
    # plt.plot([first_stretch, second_stretch], [0,0], "+r")
    # plt.show()
        
    # left_slope = slope_left(vec)
    # right_slope = slope_right(vec)

    # while left_slope < 2.0 or right_slope < 2.0:
    #     if left_slope < 2.0:
    #         img = crop_top(img, pct)
    #     if right_slope < 2.0:
    #         (img, del_y) = crop_bottom(img, pct)
    #         bottom = bottom - del_y
        
    #     cropped_equ = cv.equalizeHist(img)
    
    #     cropped_equ[cropped_equ < 225] = 0
    
    #     vec = [0] * len(cropped_equ)
    
    #     for (index, row) in enumerate(cropped_equ):
    #         vec[index] = sum(row != 0)    
        
    #     left_slope = slope_left(vec)
    #     right_slope = slope_right(vec)
    
    return (first_stretch, second_stretch)

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

def locate_fish_bounds(img, dark):
    img = np.array(img).T

    nose = 0
    tail = len(img)

    vec = [0] * len(img)

    threshold = 100 if dark else 130
    
    for (index, row) in enumerate(img):
        vec[index] = sum(row < threshold)

    for (index, num_dark) in enumerate(vec):
        if num_dark == 0:
            nose = index

        if num_dark > 10:
            break

    if dark:
        for (index, num_dark) in enumerate(vec[::-1]):
            if num_dark < 100:
                tail = len(vec) - index

            if num_dark > 100:
                break
    else:
        for (index, num_dark) in enumerate(vec[::-1]):
            if num_dark == 0:
                tail = len(vec) - index

            if num_dark > 10:
                break
 
    return (nose, tail)



def from_bottom(img):
    img_T = np.array(img)
    vec = [0] * len(img_T)
    
    for (index, col) in enumerate(img_T):
        vec[index] = sum(col > 225)

    # if the image is too dark, need to use a different thresholding method
    if np.mean(vec[0:500]) < 10:
        return None

    # find the first three zero points

    # first zero is a throw away
    first_zero_index = -1
    second_zero_index = -1
    third_zero_index = -1

    third_count_down = 100

    for (index, num_dark) in enumerate(vec):
        # stop setting first
        if num_dark > 500 and first_zero_index != -1 and second_zero_index == -1 and third_zero_index == -1:
            second_zero_index = -2

        # stop setting second
        if num_dark > 0 and vec[index + 10] == 0 and first_zero_index != -1  and second_zero_index == -2:
            second_zero_index = index + 10
            third_zero_index = -2

        # set first if second and third both == -1
        if num_dark == 0 and second_zero_index == -1 and third_zero_index == -1:
            first_zero_index = index

        # set third if third != -1
        # wait 100 pixels to set third then wait until 
        if third_zero_index == -2 and third_count_down > 0:
            third_count_down -= 1
        
        if third_count_down == 0 and num_dark > 50:
            third_count_down = -1

        if third_count_down == -1 and num_dark == 0 and third_zero_index != -1 and np.mean(vec[index: index + 20]) < 10:
            third_zero_index = index
            break

    return (second_zero_index, third_zero_index)


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


def main(img_path):
    image = cv.imread(img_path, 0)

    # rotate image if needed
    image = rotate_upright(image)

    clahe = cv.createCLAHE(clipLimit=0.5, tileGridSize=(8, 8))

    image_clahe = clahe.apply(image)

    top_bottom_tup = from_bottom(image_clahe)    

    if top_bottom_tup == None:
        (top, bottom) = crop_dark_img(image)
        dark = True
    else:
        (top, bottom) = top_bottom_tup
        dark = False

    new_image = image_clahe[top + 50: bottom + 30, :]
    (nose, tail) = locate_fish_bounds(new_image, dark)
    return (image, nose, tail, bottom, dark)

    # return (0, bottom, nose - 25, tail + 30)
'''
  This file with contain methods to detect the scale for
  pixels to cm for guppy images for measurements
  Measurements should be in mm -> cm:mm = 1:10
'''
import matplotlib.pyplot as plt
from typing import List
import numpy as np
import cv2 as cv


def _tick_seperation(bins: List[float]) -> float:
    vals = []
    for (i, x) in enumerate(bins[:-2]):
        if ((x != 0) & (bins[i + 1] != 0)):
            vals.append(bins[i + 1] - x)

    return sum(vals) / len(vals)


def _approximate_ticks(pts: List[int]) -> List[float]:
    bins = []

    cur_bin = []
    for pt in pts:
        if (len(cur_bin) == 0):
            cur_bin.append(pt)
        else:
            avg = sum(cur_bin) / len(cur_bin)
            if ((avg + 20 >= pt) & (avg - 20 <= pt)):
                cur_bin.append(pt)
            else:
                bins.append(avg)
                cur_bin.clear()
                cur_bin.append(pt)

    return bins

def remove_outliars(
    bins: List[float]
) -> List[float]:
    seps = np.ediff1d(bins)
    mean = np.mean(seps)
    std = np.std(seps)

    new_seps = []

    for sep in seps:
        if (sep < (mean + std)) and (sep > (mean - std)):
            new_seps.append(sep)

    return new_seps


def _remove_outlier_seperations(
    bins: List[float],
    avg_sep: float
) -> List[float]:
    filtered_sep = []

    i = 0

    while i < len(bins) - 1:
        sep = bins[i + 1] - bins[i]

        if (sep < (avg_sep * 1.25)):
            filtered_sep.append(sep)

        i = i + 1

    return filtered_sep


# def _detect_ruler_ticks(img, dark):
#     threshold = 100 if dark else 130

#     # clahe = cv.createCLAHE(clipLimit=0.5, tileGridSize=(8, 8))
#     if dark:
#         img = cv.equalizeHist(img)
#     else:
#         clahe = cv.createCLAHE(clipLimit=0.5, tileGridSize=(8, 8))
#         img = clahe.apply(image)

#     dark_pixels = []
#     index = 0
#     ticks = []

#     for i in range(len(img)):
#         _dark_pixels = np.array(np.where(img[i] < threshold))
#         if len(_dark_pixels[0]) > 1000:
#             ticks = _approximate_ticks(_dark_pixels[0])
#             index = i
#             break

def _detect_ruler_ticks(img, dark) -> List[float]:

    threshold_color = 100 if dark else 160
    threshold_pixels = 1000 if dark else 300


    if dark:
        img = cv.equalizeHist(img)
    else:
        img = cv.createCLAHE(clipLimit=0.5, tileGridSize=(8,8)).apply(img)

    ticks = []
    index = 0

    for i in range(len(img)):
        dark_pixels = np.array(np.where(img[i] < threshold_color))

        if len(dark_pixels[0]) > threshold_pixels:
            ticks = _approximate_ticks(dark_pixels[0])
            break

    return ticks

def main(
    img,
    bottom,
    dark
) -> float:
    img = img[bottom+50:, :]

    ticks = _detect_ruler_ticks(img, dark)

    filtered_seps = remove_outliars(ticks)
    
    seperation = np.mean(filtered_seps)
    
    # each line represents a tenth of a cm
    return seperation * 10
'''
  This file with contain methods to detect the scale for
  pixels to inch for guppy images for measurements
  Measurements should be in mm -> inch:mm = 1:25.4
'''
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
            if ((avg + 15 >= pt) & (avg - 15 <= pt)):
                cur_bin.append(pt)
            else:
                bins.append(avg)
                cur_bin.clear()
                cur_bin.append(pt)

    return bins


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


def _detect_ruler_ticks(thresholded_img) -> List[float]:
    y_value = 0
    ticks = []

    while True:
        # where the img @ the y value is dark (presumably the ticks)
        lines: List[List[int], List[int]] = np.array(
            np.where(thresholded_img[y_value] == 0))
        ticks = _approximate_ticks(lines[0])

        if len(ticks) >= 70:
            break

        y_value = y_value + 20

    return ticks


def scale_thresh(img):
    # https://en.wikipedia.org/wiki/Adaptive_histogram_equalization
    clahe = cv.createCLAHE(clipLimit=2, tileGridSize=(5, 5))
    cl1 = clahe.apply(img.copy())

    # create threshold image for scale
    scale_thresh = cv.threshold(cl1, 50, 255, cv.THRESH_BINARY)[1]

    return scale_thresh


def main(
    img,
    bottom
) -> float:
    img = scale_thresh(img[bottom + 100:, :])

    ticks = _detect_ruler_ticks(img)
    seperation = _tick_seperation(ticks)
    filtered_seps = _remove_outlier_seperations(ticks, seperation)

    seperation = sum(filtered_seps) / len(filtered_seps)

    # each line represents a tenth of an inch and inch
    return seperation * 10
'''
  This file with contain methods to detect the scale for
  pixels to inch for guppy images for measurements
  Measurements should be in mm -> inch:mm = 1:25.4
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


def _detect_ruler_ticks(img) -> List[float]:
    for i in range(len(img)):
        dark_pixels = np.array(np.where(img[i] < 130))
        ticks = _approximate_ticks(dark_pixels[0])

        if len(ticks) > 60:
            return ticks

def main(
    img,
    bottom
) -> float:
    img = img[bottom:, :]

    ticks = _detect_ruler_ticks(img)
    seperation = _tick_seperation(ticks)
    filtered_seps = _remove_outlier_seperations(ticks, seperation)

    seperation = sum(filtered_seps) / len(filtered_seps)

    # each line represents a tenth of an inch and inch
    return seperation * 10
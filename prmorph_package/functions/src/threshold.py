import cv2 as cv
import numpy as np
from numpy import uint8
from numpy.typing import NDArray
from typing import Tuple


Image = NDArray[uint8]

'''
generate_thresholds takes an image path and generates four different thresholds on the image
and returns a tuple of the four thresholds that will be returned are
equ_low_med (equalized -> threshold @ 50, 255)
clahe_high (clahe -> threshold @ 140, 255)
low (threshold @ 10,255)
equ_med (equalized -> threshold @ 75, 255)

:param image: cropped image
:param t1: bool
:param t2: bool
:param t3: bool
:param t4: bool
:rtype tuple of thresholded images:
'''


def main(
    img: Image,
    t1: bool,
    t2: bool,
    t3: bool,
    t4: bool,
    t5: bool
) -> Tuple[Image, Image, Image, Image]:
    thresh_equ = None
    thresh_cl1 = None
    low_thresh = None
    alt_thresh_equ = None
    ocr_thresh = None

    if t1 or t4:
        # equalize colors in image
        equ = _equalized_image(img)

    if t1:
        # apply threshold converting most of the fish to black
        thresh_equ = _equalized_threshold(equ)

    if t2 or t3:
        # https://en.wikipedia.org/wiki/Adaptive_histogram_equalization
        clahe = _clahe(img)

    if t2:
        # apply a softer threshold
        thresh_cl1 = _threshold_image(clahe, 140, 255)

    if t3:
        # apply a low threshold to get the darkest pixels
        low_thresh = _threshold_image(clahe, 10, 255)

    if t4:
        # create a mask to get the bottom appendage
        # apply different threshold to equalized image
        alt_thresh_equ = _threshold_image(equ, 75, 255)

    if t5:
        ocr_thresh = _ocr_processing(img)

    return (
        thresh_equ,
        thresh_cl1,
        low_thresh,
        alt_thresh_equ,
        ocr_thresh
    )


def _equalized_image(img: Image):
    # equalize the colors in the image
    return cv.equalizeHist(img.copy())


def _equalized_threshold(equalized_image: Image):
    thresh_equ = cv.threshold(equalized_image, 50, 255, cv.THRESH_BINARY)[1]

    # apply some opening to the top image
    thresh_equ = cv.morphologyEx(
        thresh_equ, cv.MORPH_OPEN, np.ones((8, 8), np.uint8))

    return thresh_equ


def _clahe(img: Image):
    # https://en.wikipedia.org/wiki/Adaptive_histogram_equalization
    clahe = cv.createCLAHE(clipLimit=2, tileGridSize=(5, 5))
    return clahe.apply(img.copy())


def _threshold_image(img, low, high):
    return cv.threshold(img, low, high, cv.THRESH_BINARY)[1]

def _ocr_processing(img: Image):
    img = cv.bitwise_not(img)
    kernel = np.ones((5,5),np.uint8)
    closing = cv.morphologyEx(img, cv.MORPH_CLOSE, kernel)

    return cv.threshold(closing, 100, 255, cv.THRESH_BINARY)[1]
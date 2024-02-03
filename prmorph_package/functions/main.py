"""this is the main exit point of all method in files from functions"""
import numpy as np
import cv2 as cv
import io
import os
import matplotlib.pyplot as plt
from .src import vision
from .src import locate_points as locate
from .src import crop_image as crop
from .src import scale
from .src import threshold as thresh
from .src import measure
from .src import landmark
from .src import trace
from .. import logging as logs

logger = logs.get_logger(__name__)

def regular_length(guppy_path: str, writer: io.TextIOWrapper, _) -> None:
    # store the file name not direct path
    guppy = guppy_path.split("/")[-1]

    logger.info(f"Computing length of {guppy}")

    image = cv.imread(guppy_path, 0)
    print(guppy_path)
    # flip = False
    # if image.shape[0] > image.shape[1]:
    #     flip = True
    #     image = cv.rotate(image, cv.ROTATE_90_COUNTERCLOCKWISE)
    #     cv.imwrite("./flipped.jpg", image)

    # use these to crop image
    (image, nose, tail, bottom, dark) = crop.main(guppy_path)
    # (top, bottom, left, right) = crop.main(guppy_path, flip)

    # crop the image with just the bottom to get the scale
    pixel_ratio = scale.main(image, bottom, dark)

    # contrast_fish = cv.createCLAHE(clipLimit=0.5, tileGridSize=(8, 8)).apply(cropped_img)
    # contrast_fish[contrast_fish < 130] = 0
    # plt.imshow(contrast_fish)
    # plt.show()

    # (equ_low_mid, clahe_mid, _, equ_mid, _) = thresh.main(
    #     cropped_img, True, True, False, True, False)
    
    # the dark pixels in the each trace
    # top_dark_pixels = np.array(np.where(equ_low_mid == 0))
    # bottom_appendage_dark_pixels = np.array(np.where(equ_mid == 0))

    # (_, _, nose, _) = locate.main(
    #     top_dark_pixels, 
    #     bottom_appendage_dark_pixels, 
    #     top_dark_pixels, 
    #     False, 
    #     False, 
    #     True, 
    #     True
    # )

    # traces = trace.main([equ_low_mid, clahe_mid, None, equ_mid], True, False, False, False)

    # """ get caudal point with landmarks """
    # landmarks = landmark.get_landmarks(
    #     traces, 
    #     [False, False, False, False, False, False, False, False, False, True, True]
    # )

    # # get the landmarks that mark the beginning of the tail fin
    # (p1, p2) = landmarks
    # # approximate teh caudal using a quadratic equation
    # caudal = locate.approximate_caudal(p1, p2)

    # calculate the length using the two points
    length = measure.regular_length(nose, tail, pixel_ratio)
    print(length)
    # write the length into the csv
    writer.write(f"{guppy},{length}\n")


"""
Use google cloud vision to detect the text in image in order to relabel images
"""
def detect_fish_id(guppy_path: str, writer: io.TextIOWrapper, out_dir: str = "./") -> None:
    # store the file name not direct path
    guppy = guppy_path.split("/")[-1]
    
    logger.info(f"Detecting fish ID from {guppy}")

    image = cv.imread(guppy_path, 0)

    (top, _, _, _) = crop.main(guppy_path)

    (_, _, _, _, ocr_img) = thresh.main(image[0:top,:], False, False, False, False, True)
    
    file_name = f'{out_dir}/temp/ocr_{guppy_path.split("/")[-1]}'
    cv.imwrite(file_name, ocr_img)

    fish_ID = vision.detect_text(file_name)

    writer.write(f"{guppy},{fish_ID}")

    os.remove(file_name)

    """ 
    add some kind of error correction, 
    we know the streams, 
    we know the potential combinations of colors and location and 
    we can find out the date 
    """
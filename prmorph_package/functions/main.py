"""this is the main exit point of all method in files from functions"""
import numpy as np
import cv2 as cv
import io
import matplotlib.pyplot as plt
import prmorph_package.functions.src.vision as vision
import prmorph_package.functions.src.locate_points as locate
import prmorph_package.functions.src.crop_image as crop
import prmorph_package.functions.src.scale as scale
import prmorph_package.functions.src.threshold as thresh
import prmorph_package.functions.src.measure as measure
import prmorph_package.config.logging as logs

logger = logs.get_logger(__name__)

def regular_length(guppy_path: str, writer: io.TextIOWrapper) -> float:
    # store the file name not direct path
    guppy = guppy_path.split("/")[-1]

    logger.info(f"Computing length of {guppy}")

    image = cv.imread(guppy_path, 0)

    # use these to crop image
    (top, bottom, left, right) = crop.main(guppy_path)

    # crop the image with just the bottom to get the scale
    pixel_ratio = scale.main(image, bottom)

    (equ_low_mid, _, _, equ_mid, _) = thresh.main(
        image[top:bottom, left:right], True, False, False, True, False)

    # the dark pixels in the each trace
    top_dark_pixels = np.array(np.where(equ_low_mid == 0))
    bottom_appendage_dark_pixels = np.array(np.where(equ_mid == 0))

    (_, _, nose, caudal) = locate.main(
        top_dark_pixels, bottom_appendage_dark_pixels, top_dark_pixels, False, False, True, True)

    length = measure.regular_length(nose, caudal, pixel_ratio)

    # write the length into the csv
    writer.write(f"{guppy},{length}\n")

    return length

def detect_fish_id(guppy_path: str, out_dir: str) -> str:
    logger.info("FISH_ID detection has not been set up yet")

    image = cv.imread(guppy_path, 0)

    (top, _, _, _) = crop.main(guppy_path)

    (_, _, _, _, ocr_img) = thresh.main(image[0:top,:], False, False, False, False, True)
    
    file_name = f'{out_dir}/temp/ocr_{guppy_path.split("/")[-1]}'
    cv.imwrite(file_name, ocr_img)

    # vision.detect_text(file_name)
    """ 
    add some kind of error correction, 
    we know the streams, 
    we know the potential combinations of colors and location and 
    we can find out the date 
    """
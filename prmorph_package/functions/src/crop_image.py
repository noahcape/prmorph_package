from typing import List, Tuple, Callable
import numpy as np
import skimage
import prmorph_package.utils as utils


Point = Tuple[int, int]
Pixels = List[Point]


'''
Method to find the last dark pixel x coordinate
on a certain y axis coordinate

:param pixels: list of dark pixels
:param y: the y coordinate to look at
:rtype int:
'''


def find_last_pixel(pixels: Pixels, y: int) -> int:
    pixels = pixels[::-1]

    for p in pixels:
        if (p[1] == int(y)):
            return p[0]

    return 0


'''
Method to remove outliers from a list, use lambdas to make decisions
about mutating lists to find target. Loop exits when stadnard deviation of
x values is less that 10.

:param pixels: list of pixels
:param move_func: lambda method to inc or decrement some number
:param move_length: lambda method to slice an array
:rtype tuple of x values and pixels
'''


def filter_outliers(
    pixels: Pixels,
    move_func: Callable[[List, int], List],
    move_length: Callable[[int, int], int]
) -> Tuple[List[int], Pixels]:
    # keep track of the standard deviation
    stdev = None

    # keep track of the numbers
    numbers = list(map(lambda x: x[0], pixels))

    # current length cutoff
    length = len(pixels)

    # length of array to inc by
    inc = int(length / 20)

    while len(numbers) > 10:
        stdev = np.std(numbers)

        if (stdev < 10):
            break

        length = move_length(inc, length)
        numbers = move_func(numbers, length)
        pixels = move_func(pixels, length)

    return (numbers, pixels)


# get the nose and tail of the fish in order to only trace between those points

def get_nose_and_tail(white_pixels: Pixels) -> Tuple[Point, Point]:
    white_pixels = list(zip(white_pixels[1], white_pixels[0]))
    sorted_pixels = sorted(white_pixels, key=lambda x: x[0])

    # clean up the last trace this might include some of the bottom pixels
    # do some standard deviation between those and the other pixels
    (first_pixels, first_pixels_xy) = filter_outliers(
        sorted_pixels[:500], lambda p, l: p[l:], lambda s, l: int(l - s))

    # with this we can get the average y value then trace to the end of the fish to get the end x value of the tail
    (x, y) = utils.get_avg_pnt(first_pixels_xy)

    last_pixel = find_last_pixel(white_pixels, y)
    avg_first = utils.get_avg(first_pixels)

    return (avg_first, last_pixel)


def get_top_crop(image):
    # convert image to b&w
    image = skimage.color.rgb2gray(image)
    # add a filter
    image = skimage.filters.gaussian(image, sigma=1)

    black_pixels = 0
    t = 0.58
    while black_pixels < 250000:
        thresh = t
        binary_mask = image <= thresh

        black_pixels = np.array(np.where(~binary_mask)).shape[1]
        t -= 0.01

    white_rows = 0
    start_looking = False
    start_column = 0
    end_column = 0

    for row in range(len(binary_mask)):
        col = None
        if (start_column == 0):
            col = binary_mask[row]
        else:
            col = binary_mask[row][start_column:end_column]

        white_pixel_count = sum(col)
        dark_pixel_count = len(col) - white_pixel_count

        if (start_column == 0 and (dark_pixel_count / white_pixel_count) > 0.1):
            dark_pixels = np.where(~col)
            start_column = dark_pixels[0][0]
            end_column = dark_pixels[0][-1]

        if (start_looking and dark_pixel_count == 0):
            white_rows += 1

        if (white_rows > 10):
            return row

        if (~start_looking and dark_pixel_count > 100):
            start_looking = True


def get_bottom_crop(image):
    # convert image to b&w
    image = skimage.color.rgb2gray(image)
    # add a filter
    image = skimage.filters.gaussian(image, sigma=1)

    # do some morphological shifting
    # https://scikit-image.org/docs/stable/api/skimage.morphology.html

    t = 0.35
    binary_mask = image >= t

    binary_mask = binary_mask[::-1]

    dark_rows = 0

    for row in range(len(binary_mask)):
        col = binary_mask[row]

        dark_pixel_count = len(col) - sum(col)

        if (dark_pixel_count > 1000):
            dark_rows += 1

        # use the first and last value of dark_pixels
        # after there have been >300 rows of high dark pixel rows
        if (dark_rows > 300):
            dark_pixels = np.where(~col)

            if (len(dark_pixels[0]) == 0):
                return len(binary_mask) - row

            diff = dark_pixels[0][-1] - dark_pixels[0][0]

            if (diff < 1000):
                return len(binary_mask) - (row + 20)


def get_left_right_crop(image):
    # convert image to b&w
    image = skimage.color.rgb2gray(image)
    # add a filter
    image = skimage.filters.gaussian(image, sigma=1)

    # do some morphological shifting
    # https://scikit-image.org/docs/stable/api/skimage.morphology.html

    t = 0.44
    binary_mask = image <= t

    white_pixels = np.array(np.where(binary_mask))

    (first, last) = get_nose_and_tail(white_pixels)

    # give a 10 pixel boundry for first and 25 for the last
    return (int(first - 25), int(last + 25))


def crop_image_height(img, top, bottom):
    image = skimage.io.imread(fname=img)

    image = image[top:bottom, :]

    return image


'''
Main method used to get the placement of the fish.
'''


def main(img_path):
    img = skimage.io.imread(img_path)
    image = skimage.exposure.rescale_intensity(img, (100, 250))

    top = get_top_crop(image)
    bottom = get_bottom_crop(image)

    image = crop_image_height(img_path, top, bottom)

    (left, right) = get_left_right_crop(image)

    return (top, bottom, left, right)

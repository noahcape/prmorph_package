import prmorph_package.utils as utils
from typing import List, Tuple

Pixel_List = Tuple[List[int], List[int]]
Averaged_Point = Tuple[float, float]


'''
Method to get points of interest, currently points of interest include:
top of dorsol fin, bottom of gonopodium/anal fin, nose and where caudal fine meets the body

:param t_b_top_pixels: thresholded top best pixels
:param t_b_bottom_pixels: thresholded bottom best pixles
:param n_t_pixels: thresholded full body bets pixels
:param get_top: bool
:param get_bottom: bool
:param get_nose: bool
:param get_tail: bool
:rtype tuple of points of interest:
'''

# TODO: fix this, it is actually bottom, top , nose, tail


def main(
    t_b_top_pixels: Pixel_List,
    t_b_bottom_pixels: Pixel_List,
    n_t_pixels: Pixel_List,
    get_top: bool,
    get_bottom: bool,
    get_nose: bool,
    get_tail: bool
) -> Tuple[Averaged_Point, Averaged_Point, Averaged_Point, Averaged_Point]:
    top = None
    bottom = None
    nose = None
    tail = None

    if get_top:
        top = utils.find_point(t_b_top_pixels, (0, 40), 1, lambda x, y: x < y)

    if get_bottom:
        bottom = utils.find_point(
            t_b_bottom_pixels, (-50, -1), 1, lambda x, y: x > y)

    if get_nose:
        nose = utils.find_point(n_t_pixels, (0, 5), 0)

    if get_tail:
        tail = utils.find_point(n_t_pixels, (-40, -1), 0)

    return (top, bottom, nose, tail)

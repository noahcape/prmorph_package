'''
This file will take nose and caudal point along
with the pixel:mm ratio and get the guppy length
'''
from typing import Tuple
from ... import utils


def regular_length(
    nose: Tuple[float, float],
    caudal: Tuple[float, float],
    pixel_inch_ratio: float,
) -> float:
    distance = utils.distance_btw_pts(nose, caudal)

    # inches:mmm -> 1:25.4
    distance_mm = (distance / pixel_inch_ratio) * 25.4

    return distance_mm
'''
This file will take nose and caudal point along
with the pixel:mm ratio and get the guppy length
'''
from typing import Tuple
from ... import utils


def regular_length(
    nose: Tuple[float, float],
    caudal: Tuple[float, float],
    pixel_ratio: float,
) -> float:
    distance = utils.distance_btw_pts(nose, caudal)

    distance_mm = (distance / pixel_ratio) * 10

    return distance_mm
#!/usr/bin/env python
# coding: utf-8
import matplotlib.pyplot as plt
from typing import Callable, List, Tuple
import numpy as np
from . import locate_points as l
from ... import utils as u


# detect the eye by finding largest cluster of dark pixels
def detect_eye(dark_pixels: List[List[int]]) -> u.Pixels:
    # sort the pixels along the x axis
    sorted_dark_pixels = np.argsort(dark_pixels[1])

    # keep track of the standard deviation
    stdev = None

    # keep track of the numbers
    numbers = None

    # number of iterations
    iteration = 0

    # current length cutoff
    length = len(sorted_dark_pixels)

    while iteration < 5:
        numbers = list(
            map(lambda x: dark_pixels[1][x], sorted_dark_pixels[:length]))

        stdev = np.std(numbers)

        if (stdev < 10):
            break

        length = int(length / 2)
        iteration += 1

    # now get all the actual points
    eye = list(map(lambda i: (
        dark_pixels[1][i], dark_pixels[0][i]), sorted_dark_pixels[:length]))

    return eye


# this only for now detects the fin gap for the fish
def detect_gaps(trace: u.Pixels, gap_num: int) -> u.Pixels:
    trace = trace if gap_num == 0 else trace[int(len(trace) / 2):]
    gaps = []
    # go from nose to tail on the top and teh fin should have a large drop
    init_point = trace[0]

    i = 1
    while i < len(trace[1:]):
        point = trace[i]
        distance = u.distance_btw_pts(init_point, point)
        if (distance > 30):
            gaps.append(init_point)
            gaps.append(point)
            return gaps
        init_point = point
        i += 1

    return None

# creates small subset of points which can be used to detected the end of the fin


def fill_gap(gap: Tuple[u.Point, u.Point], trace: u.Pixels) -> u.Pixels:
    return list(filter(
        lambda x: x[1] >= gap[0][1] and x[1] <= gap[1][1] and u.distance_btw_pts(
            x, gap[0]) < 300,
        trace))


# create the trace
def top_down_trace(points: u.Pixels, comparator: Callable[[int, int], bool]) -> u.Pixels:
    trace = []
    (cur_x, cur_y) = points[0]

    for pt in points[1:]:
        (x, y) = pt
        if (x == cur_x):
            if (comparator(y, cur_y)):
                cur_x, cur_y = x, y
        else:
            trace.append((cur_x, cur_y))
            cur_x, cur_y = x, y

    return trace


# creates a trace of left to right points
def left_right_trace(points: u.Pixels) -> u.Pixels:
    trace = []
    (_, cur_y) = points[0]

    cluster = []
    for pt in points[1:]:
        (x, y) = pt
        if (y == cur_y):
            cluster.append(pt)
        else:
            if (len(cluster) > 0):
                min_val = u.choose_value(
                    lambda val_1, val_2: val_1[0] < val_2[0], cluster)
                max_val = u.choose_value(
                    lambda val_1, val_2: val_1[0] > val_2[0], cluster)
                trace.append(min_val)
                trace.append(max_val)
            _, cur_y = x, y
            cluster = []
            cluster.append((x, y))

    return trace


def trace_helper(
    pixel_l: List[List[int]],
    filterer: Callable[[u.Point], bool],
    axis: int,
    comparator: Callable[[int, int], bool] = None
) -> u.Pixels:
    pixels = u.u_zip(pixel_l)

    pixels_f = list(filter(lambda pt: filterer(pt),
                    sorted(pixels, key=lambda x: x[axis])))

    if comparator:
        trace = top_down_trace(pixels_f, comparator)
    else:
        trace = left_right_trace(pixels_f)

    return trace


def trace_top(poi: Tuple[u.Point, u.Point, u.Point, u.Point], top_p: List[List[int]], axis: int) -> u.Pixels:
    (top, _, first, last) = poi

    def _filterer(pt: Tuple[int, int]) -> bool:

        return pt[1] <= first[1] and pt[1] >= top[1] and pt[0] >= first[0] and pt[0] <= last[0]

    def _comparator(this: int, that: int) -> bool:
        return this < that

    return trace_helper(top_p, _filterer, axis, _comparator if axis == 0 else None)


def trace_bottom(poi: Tuple[u.Point, u.Point, u.Point, u.Point], bottom_p: List[List[int]], axis: int) -> u.Pixels:
    (_, bottom, first, last) = poi

    def _filterer(pt: Tuple[int, int]) -> bool:
        return pt[1] >= first[1] and pt[1] <= bottom[1] and pt[0] >= first[0] and pt[0] <= last[0]

    def _comparator(this: int, that: int) -> bool:
        return this > that

    return trace_helper(bottom_p, _filterer, axis, _comparator if axis == 0 else None)


def trace(poi: Tuple[u.Point, u.Point, u.Point, u.Point], top_p: List[List[int]], bottom_p: List[List[int]], axis: int) -> u.Pixels:
    top_trace = trace_top(poi, top_p, axis)
    bottom_trace = trace_bottom(poi, bottom_p, axis)

    return top_trace + bottom_trace[::-1]


'''
Main method to trace the fish, four traces supplied
top down trace, using top down first last method, filled
gpa trace with traces the top fin using left right first last method
the eye trace which selects the eye points, and the full left right
first last trace method.

:rtype tuple of traces:
'''

def main(thresholds, trace_1, trace_2, trace_3, trace_4):
    '''
    trace 1: full body trace used for most landmarking
    trace 2: trace for dorsal and bottom appendage
    trace 3: for the eye
    trace 4: for zeta landmark, bottom belly landmark
    '''
    
    first_trace = None
    second_trace = None
    third_trace = None
    fourth_trace = None

    (thresh_1, thresh_2, thresh_3, thresh_4) = thresholds

    top_dark_pixels = np.array(np.where(thresh_1 == 0))
    bottom_dark_pixels = np.array(np.where(thresh_2 == 0))
    eye_dark_pixels = np.array(np.where(thresh_3 == 0))
    bottom_appendage_dark_pixels = np.array(np.where(thresh_4 == 0))

    # identify the bop, bottom, nose and tail of fish
    poi = l.main(
        top_dark_pixels, 
        bottom_dark_pixels, 
        top_dark_pixels, 
        True, 
        True, 
        True, 
        True
    )

    if trace_1:
        # whole fish trace
        first_trace = trace(poi, top_dark_pixels, bottom_dark_pixels, 0)

    if trace_3:
        # get the eye from darkest pixels
        third_trace = detect_eye(eye_dark_pixels)

    if trace_4:
        # fin trace for l_zeta
        fourth_trace = trace(
            poi, top_dark_pixels, bottom_appendage_dark_pixels, 1)

    if trace_2:
        # gap 0 is the fin gap
        second_trace = fill_gap(detect_gaps(
            first_trace, 0), fourth_trace.copy())

    return (first_trace, second_trace, third_trace, fourth_trace)

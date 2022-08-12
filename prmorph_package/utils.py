import math
from typing import Any, Callable, List, Tuple, TypeVar, Union
import numpy as np

''' some aliased types and generics '''
Vector = List[Union[int, float]]
Point = Tuple[Union[int, float, Any], Union[int, float, Any]]
Pixels = List[Point]
T = TypeVar('T')


'''
Utility method to get the average tuple a list of tuples

:param arr: list of tuples
:rtype: single tuple:
'''


def get_avg_pnt(
    arr: List[Point]
) -> Tuple[Point, ...]:
    return tuple([sum(y) / len(y) for y in zip(*arr)])


'''
Utility method to get the average from a list of ints or floats

:param arr: list of floats or ints
:rtype average value
'''


def get_avg(arr: List[Union[float, int]]) -> Union[float, int]:
    return sum(arr) / len(arr)


'''
Utility method to calculate the percent difference between
two values

:param value1: int or float
:param value2: int or float
:rtype float
'''


def percent_diff(value1: Union[float, int], value2: Union[float, int]) -> float:
    diff = value2 - value1

    if (diff == 0):
        return 0
    return diff / value1


'''
Utility method to calculate the dot product between
two two-dimensional vectors

:param v1: vector one
:param v2: vector two
:rypte float:
'''


def dot_prod(v1: Vector, v2: Vector) -> float:
    # calc the dot product
    dot_product = (v1[0]*v2[0]) + (v1[1]*v2[1])

    return dot_product


'''
Utility method to calculate the magnitude of a vector

:param v: vector
:rtype float:
'''


def magnitude(v: Vector) -> float:
    return math.sqrt(math.pow(v[0], 2) + math.pow(v[1], 2))


'''
Utility method to calculate the angle between two vectors

:param v1: vector one
:param v2: vector two
'''


def angle_btw_vectors(v1: Vector, v2: Vector) -> float:
    mag1 = magnitude(v1)
    mag2 = magnitude(v2)
    dot_product = dot_prod(v1, v2)

    cos = dot_product / (mag1 * mag2)
    cos = np.clip(cos, -1, 1)

    # get the arc cos
    return np.arccos(cos)


'''
Utility method to create a vector from two points

:param pt1: point one
:param pt2: point two
:rtype vector: 2D vector
'''


def vector(pt1: Point, pt2: Point) -> Vector:
    i = pt2[0] - pt1[0]
    j = pt2[1] - pt1[1]

    return np.array([i, j])


'''
Utility method to get the min and max from a list of tuples

:param bin: list of tuples
:rtype tuple of min and max from bin
'''


def get_min_max(bin: List[Tuple[Union[int, float, Any], ...]]) -> Tuple[Union[int, float], Union[int, float]]:
    return (min(bin), max(bin))


'''
Utility method to get the distance between two points

:param pt1: from point
:param pt2: to point
:rtype float: distance
'''


def distance_btw_pts(pt1: Point, pt2: Point) -> float:
    delta_x = math.pow(pt2[0] - pt1[0], 2)
    delta_y = math.pow(pt2[1] - pt1[1], 2)

    return math.sqrt(delta_x + delta_y)


'''
Generic method to take a list of values of some lambda that acts
as a comparator to pick one value from the list

:param func: lambda picking method
:param values: list of values to pick from
:rtype one element from the list:
'''


def choose_value(func: Callable[[T, T], bool], values: List[T]) -> T:
    # initialize value
    target = values[0]

    for val in values[1:]:
        if (func(val, target)):
            target = val

    return target


'''
Utility method to zip together list of lists, product of a np.where
command on threshold images.

:param array: list of two lists
:rtype list of points:
'''


def u_zip(array: List[List[int]]) -> Pixels:
    return list(zip(array[1], array[0]))


'''
Method to filter out groups of points based on
sepcified rules in comparator

:param groups: grouped points of which to choose one from 
:param axis: which axis to compare
:param comparator: rule to compare and choose group
:rtype list of points:
'''


def _choose_group(
        groups: List[Pixels],
        axis: int,
        comparator: Callable[[int, int], bool]
) -> Pixels:
    choosen_index = 0
    choosen_val: Point = (0, 0)

    for i in range(len(groups)):
        val = choose_value(
            (lambda val1, val2: val1[axis] < val2[axis]), groups[i])

        if (choosen_val == (0, 0) or comparator(val[axis], choosen_val[axis])):
            choosen_val = val
            choosen_index = i

    return groups[choosen_index]


'''
Method to group similar points and choose a certain group
from the filtered groups

:param pixels: list of points
:param axis: axis to compare
:param comparator: lambda method to choose group
:rtype pixels:
'''


def _remove_outliers(
        pixels: Pixels,
        axis: int,
        comparator: Callable[[int, int], bool]
) -> Pixels:
    all_groups = []

    group = []
    for i in range(len(pixels[:-2])):
        distance = distance_btw_pts(pixels[i], pixels[i + 1])

        if (distance > 10):
            group.append(pixels[i])
            all_groups.append(group.copy())
            group.clear()
        else:
            group.append(pixels[i])

    if (len(group) > 0):
        all_groups.append(group.copy())

    return _choose_group(all_groups, axis, comparator)


'''
Utility method to find end points from a list of points

:param pixels: list of pixels 
:param slices: slices of list to make after zipping and sorting
:param filter_lambda: lambda to filter values
:param axis: axis to sort pixels on
:rtype points representing
'''


def find_point(
    pixels: Tuple[List[int], List[int]],
    slices: Tuple[int, int],
    axis: int,
    filter_lambda: Callable[[int, int], bool] = None
) -> Point:
    sorted_p = sorted(list(zip(pixels[1], pixels[0])), key=lambda x: x[axis])

    if filter_lambda:
        sorted_p = _remove_outliers(sorted_p, 1, filter_lambda)

    return get_avg_pnt(sorted_p[slices[0]:slices[1]])

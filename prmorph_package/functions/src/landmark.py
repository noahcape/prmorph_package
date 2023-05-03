import numpy as np
import typing as type
from ... import utils as u


'''
Landmarks well found: alpha, beta, gamma, theta one, theta two
Landmarks not well found: epsilon, delta, zeta one, zeta two, eta one, eta two
'''


"""
util method for landmarking
"""

def sustained_low_angle(trace, start):
    num_pts = 0
    i = start
    while i < len(trace[:-6]):
        if ((i - start) >= 50):
            return False

        (pt1, pt2) = (trace[i], trace[i + 5])
        v = u.vector(pt1, pt2)
        angle = u.angle_btw_vectors(np.array([-1, 0]), v)

        if (angle < 0.4):
            num_pts += 1

        if (num_pts == 50):
            return True

        i += 1


'''
Detect alpha landmark (nose)
'''


def l_alpha(trace):
    (x1, y1) = trace[0]
    (x2, y2) = trace[-1]

    if (x1 == x2):
        if (y1 < y2):
            return trace[0]
        else:
            return trace[-1]
    elif (x1 < x2):
        return trace[0]
    else:
        return trace[-1]


'''
Detect beta landmark (chin)
'''


def l_beta(trace):
    trace = trace[::-1]

    num_low_angled_diffs = 0

    i = 0
    while i < len(trace):
        (pt1, pt2, pt3) = (trace[i], trace[i + 1], trace[i + 2])
        v_0 = u.vector(pt1, pt2)
        v_1 = u.vector(pt2, pt3)
        theta = u.angle_btw_vectors(v_0, v_1)

        if num_low_angled_diffs >= 5 and theta > 1:
            return pt1

        if (theta < 1):
            num_low_angled_diffs += 1
        else:
            num_low_angled_diffs = 0

        i += 1


'''
Detect gamma landmark (eye), trace does most of the work
'''


def l_gamma(eye):
    avg_pts = u.get_avg_pnt(eye)
    return (avg_pts[0], avg_pts[1])


'''
Detect theta one landmark, top caudal fin point
'''


def l_theta_one(trace):
    # start in the middle trace
    trace = trace[len(trace) // 2:]

    i = 0
    while i < len(trace[:-6]):
        (pt1, pt2) = (trace[i], trace[i + 5])
        v = u.vector(pt1, pt2)
        angle = u.angle_btw_vectors(np.array([-1, 0]), v)

        if (angle < 0.4 and sustained_low_angle(trace, i)):
            return pt1

        i += 1


'''
Detect theta two landmark, same process as
theta one just reverse the trace. Bottom
caudal fine point
'''


def l_theta_two(trace):
    return l_theta_one(trace[::-1])



"""
Main entry point for this file, to get points
"""
def get_landmarks(
    traces: type.Tuple[u.Pixels, u.Pixels, u.Pixels, u.Pixels],
    identify_list: type.List[bool]
) -> type.List[type.Tuple[float, float]]:
    '''
    trace 0: alpha, beta, deta, theta
    trace 1: ?
    trace 2: gamma
    trace 3: ?
    '''
    (trace_0, trace_1, trace_2, trace_3) = traces

    (alpha,
     beta,
     gamma,
     delta,
     epsilon,
     zeta_one,
     zeta_two,
     eta_one,
     eta_two,
     theta_one,
     theta_two) = identify_list

    # store landmarks here
    landmarks: type.List[type.Tuple[float, float]] = []

    if alpha:
        landmarks.append(l_alpha(trace_0))

    if beta:
        landmarks.append(l_beta(trace_0))

    if gamma:
        landmarks.append(l_gamma(trace_2))

    if theta_one:
        landmarks.append(l_theta_one(trace_0))

    if theta_two:
        landmarks.append(l_theta_two(trace_0))

    return landmarks

# from https://gist.github.com/robweychert/7efa6a5f762207245646b16f29dd6671

import math


def linear(t):
    return t


def ease_in_sine(t):
    return -math.cos(t * math.pi / 2) + 1


def ease_out_sine(t):
    return math.sin(t * math.pi / 2)


def ease_in_out_sine(t):
    return -(math.cos(math.pi * t) - 1) / 2


def ease_in_quad(t):
    return t * t


def ease_out_quad(t):
    return -t * (t - 2)


def ease_in_out_quad(t):
    t *= 2
    if t < 1:
        return t * t / 2
    else:
        t -= 1
        return -(t * (t - 2) - 1) / 2


def ease_in_cubic(t):
    return t * t * t


def ease_out_cubic(t):
    t -= 1
    return t * t * t + 1


def ease_in_out_cubic(t):
    t *= 2
    if t < 1:
        return t * t * t / 2
    else:
        t -= 2
        return (t * t * t + 2) / 2


def ease_in_quart(t):
    return t * t * t * t


def ease_out_quart(t):
    t -= 1
    return -(t * t * t * t - 1)


def ease_in_out_quart(t):
    t *= 2
    if t < 1:
        return t * t * t * t / 2
    else:
        t -= 2
        return -(t * t * t * t - 2) / 2


def ease_in_quint(t):
    return t * t * t * t * t


def ease_out_quint(t):
    t -= 1
    return t * t * t * t * t + 1


def ease_in_out_quint(t):
    t *= 2
    if t < 1:
        return t * t * t * t * t / 2
    else:
        t -= 2
        return (t * t * t * t * t + 2) / 2


def ease_in_expo(t):
    return math.pow(2, 10 * (t - 1))


def ease_out_expo(t):
    return -math.pow(2, -10 * t) + 1


def ease_in_out_expo(t):
    t *= 2
    if t < 1:
        return math.pow(2, 10 * (t - 1)) / 2
    else:
        t -= 1
        return -math.pow(2, -10 * t) - 1


def ease_in_circ(t):
    return 1 - math.sqrt(1 - t * t)


def ease_out_circ(t):
    t -= 1
    return math.sqrt(1 - t * t)


def ease_in_out_circ(t):
    t *= 2
    if t < 1:
        return -(math.sqrt(1 - t * t) - 1) / 2
    else:
        t -= 2
        return (math.sqrt(1 - t * t) + 1) / 2

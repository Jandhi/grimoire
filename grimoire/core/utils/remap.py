from typing import Callable


def remap(
    func: Callable[[any], float], mapping: Callable[[float], float]
) -> Callable[[any], float]:
    def new_func(*args, **kwargs):
        return mapping(func(*args, **kwargs))

    return new_func


# Remaps function such that it evaluates to 0 under a threshold T and scales linear from 0.0 to 1.0 above it
#
#             ---                  /
#          ---                    /
#       ---        ->            /
#    ---                        /
# ---                 ----------
#                              ^
#                              T
def remap_threshold_high(
    func: Callable[[any], float], threshold: float
) -> Callable[[any], float]:
    def mapping(value: float) -> float:
        if value < threshold:
            return 0
        else:
            return (value - threshold) / (1.0 - threshold)

    return remap(func, mapping)


# Remaps function such that it evaluates to 1 over a threshold T and scales linear from 0.0 to 1.0 below it
#
#             ---         --------------
#          ---           /
#       ---        ->   /
#    ---               /
# ---                 /
#                         ^
#                         T
def remap_threshold_low(
    func: Callable[[any], float], threshold: float
) -> Callable[[any], float]:
    def mapping(value: float) -> float:
        if value > threshold:
            return 1
        else:
            return value / threshold

    return remap(func, mapping)

from typing import Tuple
from enum import Enum

class Axis(Enum):
    LENGTH = 0
    WIDTH = 1
    HEIGHT = 2

PRECISION = 0

def valid_axis(axises:Tuple[Axis, Axis, Axis]):
    assert len(axises) == 3
    valid = False
    if Axis.LENGTH in axises and Axis.WIDTH in axises and Axis.HEIGHT in axises:
        valid = True
    return valid
from Common import *
from typing import Any, List, Tuple

def valid_axis(axises:Tuple[Axis, Axis, Axis]):
    assert len(axises) == 3
    valid = False
    if Axis.LENGTH in axises and Axis.WIDTH in axises and Axis.HEIGHT in axises:
        valid = True
    return valid

def lwh_to_axis(axises:Tuple[Axis, Axis, Axis]) -> List[int]:
    axis_map = []
    for axis in axises:
        if axis == Axis.LENGTH:
            axis_map.append(0)
        if axis == Axis.WIDTH:
            axis_map.append(1)
        if axis == Axis.HEIGHT:
            axis_map.append(2)
    return axis_map

def axis_to_lwh(axises:Tuple[Axis, Axis, Axis]) -> List[int]:
    lwh_map = [None, None, None]
    for idx, axis in enumerate(axises):
        if axis == Axis.LENGTH:
            lwh_map[0] = idx
        if axis == Axis.WIDTH:
            lwh_map[1] = idx
        if axis == Axis.HEIGHT:
            lwh_map[2] = idx
    return lwh_map

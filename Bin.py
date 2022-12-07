from Common import *
from typing import Any, List, Tuple
import utils

class Bin:
    def __init__(self, l:float, w:float, h:float, precision:int=PRECISION):
        self.l = l
        self.w = w
        self.h = h
        self.precision = precision

    def __str__(self):
        format_ctrl = "({{0:.{0}f}},{{1:.{0}f}},{{2:.{0}f}})".format(self.precision)
        return format_ctrl.format(self.l, self.w, self.h)

    def __repr__(self):
        format_ctrl = "[{{0:.{0}f}}({{3:d}}),{{1:.{0}f}}({{4:d}}),{{2:.{0}f}}({{5:d}})]".format(self.precision)
        return format_ctrl.format(self.l, self.w, self.h,
                                  self.length, self.width, self.height)

    @property
    def length(self):
        return utils.math_utils.to_precision(self.l, self.precision)

    @property 
    def width(self):
        return utils.math_utils.to_precision(self.w, self.precision)

    @property
    def height(self):
        return utils.math_utils.to_precision(self.h, self.precision)

    
    def axis_sort(self, axises:Tuple[Axis, Axis, Axis], ascending:bool=True) -> bool:
        if not utils.axis_utils.valid_axis(axises):
            raise ValueError("Axises are not valid!")
        sorted_axises = sorted([self.l, self.w, self.h], reverse=(not ascending))
        lwh_map = [None, None, None]
        for idx, axis in enumerate(axises):
            if axis == Axis.LENGTH:
                lwh_map[0] = idx
            if axis == Axis.WIDTH:
                lwh_map[1] = idx
            if axis == Axis.HEIGHT:
                lwh_map[2] = idx
        self.l, self.w, self.h = sorted_axises[lwh_map[0]],sorted_axises[lwh_map[1]],sorted_axises[lwh_map[2]]
                


       
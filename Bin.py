from Common import *
import utils
from typing import Any, List, Tuple

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

    @property
    def size_list(self):
        return [self.length, self.width, self.height]
    
    def axis_sort(self, axises:Tuple[Axis, Axis, Axis], ascending:bool=True) -> bool:
        if not utils.axis_utils.valid_axis(axises):
            raise ValueError("Axises are not valid!")
        sorted_axises = sorted([self.l, self.w, self.h], reverse=(not ascending))
        self.l, self.w, self.h = utils.axis_utils.axis_to_lwh(sorted_axises, axises)

    def axis_transform(self, axises:Tuple[Axis, Axis, Axis]) -> bool:
        self.l, self.w, self.h = utils.axis_utils.axis_to_lwh([self.l, self.w, self.h], axises)
                


       
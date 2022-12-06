from typing import Any, List, Tuple
from Bin import Bin
import numpy as np
from Common import *
import utils

class Container:
    def __init__(self, ml:float, mw:float, mh:float, precision:int=PRECISION):
        self.ml = ml
        self.mw = mw
        self.mh = mh
        self.precision = precision
        self.construct_space()

    @property
    def max_length(self):
        return utils.math_utils.to_precision(self.ml, self.precision)

    @property
    def max_width(self):
        return utils.math_utils.to_precision(self.mw, self.precision)

    @property
    def max_height(self):
        return utils.math_utils.to_precision(self.mh, self.precision)

    def __str__(self):
        format_ctrl = "({{0:.{0}f}},{{1:.{0}f}},{{2:.{0}f}})".format(self.precision)
        return format_ctrl.format(self.ml, self.mw, self.mh)

    def __repr__(self):
        format_ctrl = "[{{0:.{0}f}}({{3:d}}),{{1:.{0}f}}({{4:d}}),{{2:.{0}f}}({{5:d}})]".format(self.precision)
        return format_ctrl.format(self.ml, self.mw, self.mh,
                                  self.max_length, self.max_width, self.max_height)

    def construct_space(self) -> None:
        self.space = np.zeros((self.max_length, self.max_width, self.max_height), dtype=np.int32)

    @property
    def space_utilization(self) -> np.float32:
        return np.sum(self.space)/np.sum(np.ones_like(self.space))

    def print_2D_matrix(self, matrix:Any, compact:bool=False):
        map_str = str(matrix).replace("],","],\n").replace("'","").replace(",","").replace("1","█")
        if compact:
            map_str = map_str.replace(" ","").replace("[[","[").replace("]]","]")
        return map_str

    # h     h     w    
    # ↑     ↑     ↑    
    # |-→ w |-→ l |-→ l
    #   l     w     h
    def print_2D_slice(self, asix: Axis, slice:int, compact:bool=False):
        if asix == Axis.LENGTH:
            matrix = np.transpose(self.space[slice,:,:])
        elif asix == Axis.WIDTH:
            matrix = np.transpose(self.space[:,slice,:])
        elif asix == Axis.HEIGHT:
            matrix = np.transpose(self.space[:,:,slice])
        matrix = matrix[::-1,:]
        matrix = matrix.tolist()
        matrix_str = self.print_2D_matrix(matrix,compact)
        print(matrix_str)

    def within(self, new_bin:Bin, position:Tuple[int,int,int]):
        is_within = \
        (0 <= position[0] and position[0] <= self.space.shape[0]) and \
        (1 <= position[0] + new_bin.length and position[0] + new_bin.length <= self.space.shape[0]) and \
        (0 <= position[1] and position[1] <= self.space.shape[1]) and \
        (1 <= position[1] + new_bin.width and position[1] + new_bin.width <= self.space.shape[1]) and \
        (0 <= position[2] and position[2] <= self.space.shape[2]) and \
        (1 <= position[2] + new_bin.height and position[2] + new_bin.height <= self.space.shape[2])
        return is_within

    def will_fall(self, new_bin:Bin, position:Tuple[int,int,int]):
        lower_level = position[2] - 1
        if lower_level == -1:
            return False
        else:
            lower_level_slice = self.space[:,:,lower_level]
            bin_slice = lower_level_slice[position[0]:position[0]+new_bin.length,position[1]:position[1]+new_bin.width]
            # if np.sum(bin_slice)/np.sum(np.ones_like(bin_slice)) >= 1/2:
            #     return False
            if bin_slice[0,0] == 1 and bin_slice[0,-1] == 1 and bin_slice[-1,0] == 1 and bin_slice[-1,-1] == 1:
                return False  
        return True  
            
        
    def put(self, new_bin:Bin, position:Tuple[int,int,int]) -> bool:
        if not self.within(new_bin, position):
            return False
        if self.will_fall(new_bin, position):
            return False
        if np.sum(self.space[position[0]:position[0]+new_bin.length,
                             position[1]:position[1]+new_bin.width,
                             position[2]:position[2]+new_bin.height]) == 0:
            self.space[position[0]:position[0]+new_bin.length,
                       position[1]:position[1]+new_bin.width,
                       position[2]:position[2]+new_bin.height] = 1
            return True
        else:
            return False

    def greedy_find(self, new_bin:Bin, axises:Tuple[Axis, Axis, Axis]) -> Tuple[int,int,int]:
        if not valid_axis(axises):
            raise ValueError("Axises are not valid!")
        # axises = reversed(axises)
        search_order = []
        order_map = []
        for axis in axises:
            if axis == Axis.LENGTH:
                order_map.append(0)
            if axis == Axis.WIDTH:
                order_map.append(1)
            if axis == Axis.HEIGHT:
                order_map.append(2)
        lwh_map = [None, None, None]
        for idx, axis in enumerate(axises):
            if axis == Axis.LENGTH:
                lwh_map[0] = idx
            if axis == Axis.WIDTH:
                lwh_map[1] = idx
            if axis == Axis.HEIGHT:
                lwh_map[2] = idx
        search_axises = [self.max_length, self.max_width, self.max_height]
        search_order = [search_axises[order_map[0]],search_axises[order_map[1]],search_axises[order_map[2]]]

        for axis_0 in range(search_order[0]):
            for axis_1 in range(search_order[1]):
                for axis_2 in range(search_order[2]):
                    axis_index_list = [axis_0, axis_1, axis_2]
                    idx_length = axis_index_list[lwh_map[0]]
                    idx_width = axis_index_list[lwh_map[1]]
                    idx_height = axis_index_list[lwh_map[2]]
                    if self.put(new_bin,(idx_length, idx_width, idx_height)):
                        return (idx_length, idx_width, idx_height)
                    else:
                        pass
        return None
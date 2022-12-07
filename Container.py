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

    def within(self, new_bin:Bin, position:Tuple[int,int,int]) -> Tuple[bool, bool, bool]:
        length_within = \
        (0 <= position[0] and position[0] <= self.space.shape[0]) and \
        (1 <= position[0] + new_bin.length and position[0] + new_bin.length <= self.space.shape[0])
        width_within = \
        (0 <= position[1] and position[1] <= self.space.shape[1]) and \
        (1 <= position[1] + new_bin.width and position[1] + new_bin.width <= self.space.shape[1])
        height_within = \
        (0 <= position[2] and position[2] <= self.space.shape[2]) and \
        (1 <= position[2] + new_bin.height and position[2] + new_bin.height <= self.space.shape[2])
        return length_within, width_within, height_within

    def stable(self, new_bin:Bin, position:Tuple[int,int,int]):
        lower_level = position[2] - 1
        if lower_level == -1:
            return True
        else:
            lower_level_slice = self.space[:,:,lower_level]
            bin_slice = lower_level_slice[position[0]:position[0]+new_bin.length,position[1]:position[1]+new_bin.width]
            # if np.sum(bin_slice)/np.sum(np.ones_like(bin_slice)) >= 1/2:
            #     return False
            if bin_slice[0,0] == 1 and bin_slice[0,-1] == 1 and bin_slice[-1,0] == 1 and bin_slice[-1,-1] == 1:
                return True  
        return False  
            
        
    def put(self, new_bin:Bin, position:Tuple[int,int,int]) -> bool:
        within = self.within(new_bin, position)
        if not all(within):
            return (*within, True, True)
        if not self.stable(new_bin, position):
            return (True, True, True, False, True)
        if np.sum(self.space[position[0]:position[0]+new_bin.length,
                             position[1]:position[1]+new_bin.width,
                             position[2]:position[2]+new_bin.height]) == 0:
            self.space[position[0]:position[0]+new_bin.length,
                       position[1]:position[1]+new_bin.width,
                       position[2]:position[2]+new_bin.height] = 1
            return (True, True, True, True, True)
        else:
            return (True, True, True, True, False)

    def greedy_find(self, new_bin:Bin, axises:Tuple[Axis, Axis, Axis], start_point:Tuple[int,int,int]=(0,0,0)) -> Tuple[int,int,int]:
        if not utils.axis_utils.valid_axis(axises):
            raise ValueError("Axises are not valid!")
        # axises = reversed(axises)
        search_order = []
        axis_map = utils.axis_utils.lwh_to_axis(axises)
        lwh_map = utils.axis_utils.axis_to_lwh(axises)
        search_axises = [self.max_length, self.max_width, self.max_height]
        search_order = [search_axises[axis_map[0]],search_axises[axis_map[1]],search_axises[axis_map[2]]]

        # TODO 改判断逻辑
        for axis_0 in range(start_point[0], search_order[0]):
            for axis_1 in range(start_point[1], search_order[1]):
                for axis_2 in range(start_point[2], search_order[2]):
                    axis_index_list = [axis_0, axis_1, axis_2]
                    idx_length = axis_index_list[lwh_map[0]]
                    idx_width = axis_index_list[lwh_map[1]]
                    idx_height = axis_index_list[lwh_map[2]]
                    results = self.put(new_bin,(idx_length, idx_width, idx_height))
                    neg_result = [not result for result in results]
                    skip_axis = neg_result[axis_map[0]], neg_result[axis_map[1]], neg_result[axis_map[2]]
                    if any(skip_axis[:3]):
                        break
                    elif any(neg_result):
                        continue
                    else:
                        return (idx_length, idx_width, idx_height) 
                if any(skip_axis[:2]):
                    break 
            if any(skip_axis[:1]):
                break
        return None
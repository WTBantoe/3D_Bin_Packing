from Common import *
import utils

from typing import Any, List, Tuple
from Bin import Bin
import numpy as np

class Container:
    def __init__(self, ml:float, mw:float, mh:float, precision:int=PRECISION):
        self.ml = ml
        self.mw = mw
        self.mh = mh
        self.precision = precision
        self.construct_space()
        self.next_length_points = []
        self.next_width_points = []
        self.next_height_points = []

    @property
    def max_length(self):
        return utils.math_utils.to_precision(self.ml, self.precision)

    @property
    def max_width(self):
        return utils.math_utils.to_precision(self.mw, self.precision)

    @property
    def max_height(self):
        return utils.math_utils.to_precision(self.mh, self.precision)

    @property
    def size_list(self):
        return [self.max_length, self.max_width, self.max_height]

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

    def str_2D_matrix(self, matrix:Any, compact:bool=False):
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
        matrix_str = self.str_2D_matrix(matrix,compact)
        print(matrix_str)
    
    def point_within(self, position:Tuple[int,int,int]):
        length_within = \
        (0 <= position[0] and position[0] < self.space.shape[0]) 
        width_within = \
        (0 <= position[1] and position[1] < self.space.shape[1])
        height_within = \
        (0 <= position[2] and position[2] < self.space.shape[2])
        return length_within, width_within, height_within

    def within(self, new_bin:Bin, position:Tuple[int,int,int]) -> Tuple[bool, bool, bool]:
        length_within = \
        (0 <= position[0] and position[0] < self.space.shape[0]) and \
        (1 <= position[0] + new_bin.length and position[0] + new_bin.length <= self.space.shape[0])
        width_within = \
        (0 <= position[1] and position[1] < self.space.shape[1]) and \
        (1 <= position[1] + new_bin.width and position[1] + new_bin.width <= self.space.shape[1])
        height_within = \
        (0 <= position[2] and position[2] < self.space.shape[2]) and \
        (1 <= position[2] + new_bin.height and position[2] + new_bin.height <= self.space.shape[2])
        return length_within, width_within, height_within

    def stable(self, new_bin:Bin, position:Tuple[int,int,int], strict:bool=True):
        lower_level = position[2] - 1
        if lower_level == -1:
            return True
        else:
            lower_level_slice = self.space[:,:,lower_level]
            bin_slice = lower_level_slice[position[0]:position[0]+new_bin.length,position[1]:position[1]+new_bin.width]
            # if np.sum(bin_slice)/np.sum(np.ones_like(bin_slice)) >= 1/2:
            #     return False
            if strict:
                if bin_slice[0,0] == 1 and bin_slice[0,-1] == 1 and bin_slice[-1,0] == 1 and bin_slice[-1,-1] == 1:
                    return True
            else:
                if np.sum(bin_slice) > 0:
                    return True 
        return False  
               
    def put(self, new_bin:Bin, position:Tuple[int,int,int], strict:bool = True, just_try:bool = False) -> bool:
        within = self.within(new_bin, position)
        if not all(within):
            return (*within, True, True)
        if not self.stable(new_bin, position, strict):
            return (True, True, True, False, True)
        if np.sum(self.space[position[0]:position[0]+new_bin.length,
                             position[1]:position[1]+new_bin.width,
                             position[2]:position[2]+new_bin.height]) and not just_try == 0:
            self.space[position[0]:position[0]+new_bin.length,
                       position[1]:position[1]+new_bin.width,
                       position[2]:position[2]+new_bin.height] = 1
            return (True, True, True, True, True)
        else:
            return (True, True, True, True, False)

    def greedy_find_part(self, new_bin:Bin, axises:Tuple[Axis, Axis, Axis], start_point:Tuple[int,int,int]=(0,0,0), strict:bool=True) -> Tuple[int,int,int]:
        if not utils.axis_utils.valid_axis(axises):
            raise ValueError("Axises are not valid!")
        search_lwh = [self.max_length, self.max_width, self.max_height]
        search_axis = utils.axis_utils.lwh_to_axis(search_lwh, axises)
        axis_start_point = utils.axis_utils.lwh_to_axis(start_point, axises)

        for axis_0 in range(axis_start_point[0], search_axis[0]):
            for axis_1 in range(axis_start_point[1], search_axis[1]):
                for axis_2 in range(axis_start_point[2], search_axis[2]):
                    axis_index_list = [axis_0, axis_1, axis_2]
                    idx_length, idx_width, idx_height = utils.axis_utils.axis_to_lwh(axis_index_list, axises)
                    results = self.put(new_bin, (idx_length, idx_width, idx_height), strict)
                    neg_result = [not result for result in results]
                    skip_axis = utils.axis_utils.lwh_to_axis(neg_result[:3], axises)
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

    # FIXME 需要优化逻辑，放置一个箱子后待放置点的选择目前存在错误
    def greedy_find_with_heuristics(self, new_bin:Bin, axises:Tuple[Axis, Axis, Axis], try_rotate:bool=True, strict:bool=True) -> Tuple[int, int, int]:
        lwh_list = [self.next_length_points, self.next_width_points, self.next_height_points]
        axis_map = utils.axis_utils.lwh_to_axis_map(axises)
        axis_list = [lwh_list[axis_map[0]], lwh_list[axis_map[1]], lwh_list[axis_map[2]]]
        axis_list.reverse()
        axis_len_list = [len(axis_list[0]), len(axis_list[1]), len(axis_list[2])]
        next_points = []
        next_points.extend(axis_list[0])
        next_points.extend(axis_list[1])
        next_points.extend(axis_list[2]) 
        if next_points == []:
            bin_location = self.greedy_find_part(new_bin, axises)
        else:
            suit_one = False
            for idx_point,next_position in enumerate(next_points):
                if self.space[next_position[0],next_position[1],next_position[2]] == 1:
                    if idx_point < axis_len_list[0]:
                        axis_list[0].remove(next_position)
                    elif idx_point < axis_len_list[0] + axis_len_list[1]:
                        axis_list[1].remove(next_position)
                    elif idx_point < axis_len_list[0] + axis_len_list[1] + axis_len_list[2]:
                        axis_list[2].remove(next_position)
                    continue
                suit = False
                if try_rotate:
                    for idx_axis, axis_type in enumerate(utils.axis_utils.full_axis_type()):
                        copy_bin = Bin(new_bin.l, new_bin.w, new_bin.h, self.precision)
                        copy_bin.axis_transform(axis_type)
                        results = self.put(copy_bin, next_position, strict)
                        if all(results):
                            if idx_axis != 0:
                                logger.info(f"Rotate bin to {axis_type}")
                            bin_location = next_position
                            suit = True
                            break
                else:
                    results = self.put(new_bin, next_position, strict)
                    if all(results):
                        bin_location = next_position
                        suit = True
                if suit:
                    suit_one = True
                    break
            if not suit_one:
                bin_location = self.greedy_find_part(new_bin, axises)
        length_candidates = [(bin_location[0] + new_bin.length, bin_location[1], bin_location[2]),
                             (bin_location[0] + new_bin.length, bin_location[1] + new_bin.width, bin_location[2]),
                             (bin_location[0] + new_bin.length, bin_location[1], bin_location[2] + new_bin.height)]
        width_candidates = [(bin_location[0], bin_location[1] + new_bin.width, bin_location[2]),
                            (bin_location[0] + new_bin.length, bin_location[1] + new_bin.width, bin_location[2]),
                            (bin_location[0], bin_location[1] + new_bin.width, bin_location[2] + new_bin.height)]
        height_candidates = [(bin_location[0], bin_location[1], bin_location[2] + new_bin.height),
                             (bin_location[0] + new_bin.length, bin_location[1], bin_location[2] + new_bin.height),
                             (bin_location[0], bin_location[1] + new_bin.width, bin_location[2] + new_bin.height)]
        length_candidates = length_candidates[:1]
        width_candidates = width_candidates[:1]
        height_candidates = height_candidates[:1]
        for length_candidate in length_candidates:
            if all(self.point_within(length_candidate)) and \
            self.space[length_candidate[0],length_candidate[1],length_candidate[2]] != 1:
                self.next_length_points.append(length_candidate)
        for width_candidate in width_candidates:
            if all(self.point_within(width_candidate)) and \
            self.space[width_candidate[0],width_candidate[1],width_candidate[2]] != 1:
                self.next_width_points.append(width_candidate)
        for height_candidate in height_candidates: 
            if all(self.point_within(height_candidate)) and \
            self.space[height_candidate[0],height_candidate[1],height_candidate[2]] != 1:
                self.next_height_points.append(height_candidate)
        return bin_location

    def sub_space_find(self, new_bin:Bin):
        pass
                    
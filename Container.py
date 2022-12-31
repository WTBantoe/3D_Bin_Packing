from Common import *
import utils

from typing import Any, List, Tuple
from Bin import Bin
import numpy as np

# TODO 添加按历史搜索功能
# TODO 添加按起始点搜索功能
class Container:
    def __init__(self, ml:float, mw:float, mh:float, precision:int=PRECISION):
        self.ml = ml
        self.mw = mw
        self.mh = mh
        self.precision = precision
        self.space = self.construct_space()
        self.envelope_space = self.construct_space()
        self.simple_space = self.construct_simple_space()
        self.next_length_points = []
        self.next_width_points = []
        self.next_height_points = []
        self.candidates_points = []
        self.search_history = []

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

    @property
    def volumn(self):
        return self.max_length * self.max_width * self.max_height
    
    def __str__(self):
        format_ctrl = "({{0:.{0}f}},{{1:.{0}f}},{{2:.{0}f}})".format(self.precision)
        return format_ctrl.format(self.ml, self.mw, self.mh)

    def __repr__(self):
        format_ctrl = "[{{0:.{0}f}}({{3:d}}),{{1:.{0}f}}({{4:d}}),{{2:.{0}f}}({{5:d}})]".format(self.precision)
        return format_ctrl.format(self.ml, self.mw, self.mh,
                                  self.max_length, self.max_width, self.max_height)

    def construct_space(self) -> np.ndarray:
        return np.zeros((self.max_length, self.max_width, self.max_height), dtype=np.int32)

    def construct_simple_space(self) -> np.ndarray:
        return np.zeros((self.max_length, self.max_width), dtype=np.int32)

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
    def print_2D_slice(self, asix: Axis, slice_idx:int, compact:bool=False):
        if asix == Axis.LENGTH:
            matrix = np.transpose(self.space[slice_idx,:,:])
        elif asix == Axis.WIDTH:
            matrix = np.transpose(self.space[:,slice_idx,:])
        elif asix == Axis.HEIGHT:
            matrix = np.transpose(self.space[:,:,slice_idx])
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

    def stable(self, new_bin:Bin, position:Tuple[int,int,int], strict_level:int=3):
        lower_level = position[2] - 1
        if lower_level == -1:
            return True
        else:
            lower_level_slice = self.space[:,:,lower_level]
            bin_slice = lower_level_slice[position[0]:position[0]+new_bin.length,position[1]:position[1]+new_bin.width]
            # if np.sum(bin_slice)/np.sum(np.ones_like(bin_slice)) >= 1/2:
            #     return False
            if strict_level == 3:
                if bin_slice[0,0] == 1 and bin_slice[0,-1] == 1 and bin_slice[-1,0] == 1 and bin_slice[-1,-1] == 1:
                    return True
            elif strict_level == 2:
                if np.sum(bin_slice) > 0:
                    return True 
            elif strict_level == 1:
                if np.sum(lower_level_slice) > 0:
                    return True
            elif strict_level == 0:
                return True
        return False  

    def volumn_check(self, new_bin:Bin):
        remain_space = self.volumn - np.sum(self.space)
        if remain_space < new_bin.volume:
            return False
        else:
            return True
               
    def put(self, new_bin:Bin, position:Tuple[int,int,int], strict_level:int=3, just_try:bool=False) -> bool:
        within = self.within(new_bin, position)
        if not all(within):
            return (*within, True, True)
        if not self.stable(new_bin, position, strict_level):
            return (True, True, True, False, True)
        if np.sum(self.space[position[0]:position[0]+new_bin.length,
                             position[1]:position[1]+new_bin.width,
                             position[2]:position[2]+new_bin.height])  == 0:
            if not just_try:
                self.space[position[0]:position[0]+new_bin.length,
                           position[1]:position[1]+new_bin.width,
                           position[2]:position[2]+new_bin.height] = 1
                self.simple_space[position[0]:position[0]+new_bin.length,
                                   position[1]:position[1]+new_bin.width] = position[2]+new_bin.height
                self.envelope_space[:position[0]+new_bin.length,
                                   :position[1]+new_bin.width,
                                   :position[2]+new_bin.height] = 1
            return (True, True, True, True, True)            
        else:
            return (True, True, True, True, False)

    def find_envelope_in_slice(self,asix: Axis, slice_idx:int):
        if asix == Axis.LENGTH:
            matrix = self.envelope_space[slice_idx,:,:]
        elif asix == Axis.WIDTH:
            matrix = self.envelope_space[:,slice_idx,:]
        elif asix == Axis.HEIGHT:
            matrix = self.envelope_space[:,:,slice_idx]
        envelopes = []
        for x in range(len(matrix)):
            zero_idx = np.where(matrix[x]==0)[0]
            if len(zero_idx) == 0:
                return envelopes
            first_0 = np.min(zero_idx)
            if envelopes == []:
                envelopes.append((x, first_0))
            if first_0 == envelopes[-1][1]:
                continue
            else:
                envelopes.append((x, first_0))
        if asix == Axis.LENGTH:
            envelopes = [(slice_idx, envelope[0], envelope[1]) for envelope in envelopes]
        elif asix == Axis.WIDTH:
            envelopes = [(envelope[0], slice_idx, envelope[1]) for envelope in envelopes]
        elif asix == Axis.HEIGHT:
            envelopes = [(envelope[0], envelope[1], slice_idx) for envelope in envelopes]
        copy_envelopes = [envelope for envelope in envelopes]
        for envelope in copy_envelopes:
            near = 0
            if envelope[0] == 0 or self.envelope_space[envelope[0]-1,envelope[1],envelope[2]] == 1:
                near += 1
            if envelope[1] == 0 or self.envelope_space[envelope[0],envelope[1]-1,envelope[2]] == 1:
                near += 1  
            if envelope[2] == 0 or self.envelope_space[envelope[0],envelope[1],envelope[2]-1] == 1:
                near += 1  
            if near != 3:
                envelopes.remove(envelope)
        return envelopes          

    def add_next_points(self, bin_place:Tuple[int,int,int], new_bin:Bin):
        length_points = [(bin_place[0] + new_bin.length, bin_place[1], bin_place[2]),
                             (bin_place[0] + new_bin.length, bin_place[1] + new_bin.width, bin_place[2]),
                             (bin_place[0] + new_bin.length, bin_place[1], bin_place[2] + new_bin.height)]
        width_points = [(bin_place[0], bin_place[1] + new_bin.width, bin_place[2]),
                            (bin_place[0] + new_bin.length, bin_place[1] + new_bin.width, bin_place[2]),
                            (bin_place[0], bin_place[1] + new_bin.width, bin_place[2] + new_bin.height)]
        height_points = [(bin_place[0], bin_place[1], bin_place[2] + new_bin.height),
                             (bin_place[0] + new_bin.length, bin_place[1], bin_place[2] + new_bin.height),
                             (bin_place[0], bin_place[1] + new_bin.width, bin_place[2] + new_bin.height)]
        length_points = length_points[:1]
        width_points = width_points[:1]
        height_points = height_points[:1]
        for length_point in length_points:
            if all(self.point_within(length_point)):
                self.next_length_points.append(length_point)
        for width_point in width_points:
            if all(self.point_within(width_point)):
                self.next_width_points.append(width_point)
        for height_point in height_points: 
            if all(self.point_within(height_point)):
                self.next_height_points.append(height_point)
        self.clear_occupied_points()
        self.clear_duplicate_points()

    def clear_occupied_points(self):
        clear_idx = []
        for idx, point in enumerate(self.next_length_points):
            if self.space[point[0],point[1],point[2]] == 1:
                clear_idx.append(idx)
        idx_offset = 0
        for idx in clear_idx:
            self.next_length_points.pop(idx - idx_offset)
            idx_offset += 1  

        clear_idx = []
        for idx, point in enumerate(self.next_width_points):
            if self.space[point[0],point[1],point[2]] == 1:
                clear_idx.append(idx)
        idx_offset = 0
        for idx in clear_idx:
            self.next_width_points.pop(idx - idx_offset)
            idx_offset += 1

        clear_idx = []
        for idx, point in enumerate(self.next_height_points):
            if self.space[point[0],point[1],point[2]] == 1:
                clear_idx.append(idx)
        idx_offset = 0
        for idx in clear_idx:
            self.next_height_points.pop(idx - idx_offset)
            idx_offset += 1            

    def clear_duplicate_points(self):
        points = []
        
        length_points = []
        for idx, point in enumerate(self.next_length_points):
            already_in = False
            for in_point in points:
                if point[0] == in_point[0] and \
                   point[1] == in_point[1] and \
                   point[2] == in_point[2]:
                       already_in = True
                       break
            if not already_in:
                points.append(point)
                length_points.append(point)
        self.next_length_points = length_points

        width_points = []
        for idx, point in enumerate(self.next_width_points):
            already_in = False
            for in_point in points:
                if point[0] == in_point[0] and \
                   point[1] == in_point[1] and \
                   point[2] == in_point[2]:
                       already_in = True
                       break
            if not already_in:
                points.append(point)
                width_points.append(point)  
        self.next_width_points = width_points

        height_points = []
        for idx, point in enumerate(self.next_height_points):
            already_in = False
            for in_point in points:
                if point[0] == in_point[0] and \
                   point[1] == in_point[1] and \
                   point[2] == in_point[2]:
                       already_in = True
                       break
            if not already_in:
                points.append(point)
                height_points.append(point)  
        self.next_height_points = height_points
        
    def add_candidates(self, bin_place:Tuple[int,int,int], new_bin:Bin):
        length_slice = bin_place[0] + new_bin.length
        width_slice = bin_place[1] + new_bin.width
        height_slice = bin_place[2] + new_bin.height
        if length_slice < self.max_length:
            self.candidates_points.extend(self.find_envelope_in_slice(Axis.LENGTH, length_slice))
        if width_slice < self.max_width:
            self.candidates_points.extend(self.find_envelope_in_slice(Axis.WIDTH, width_slice))
        if height_slice < self.max_height:
            self.candidates_points.extend(self.find_envelope_in_slice(Axis.HEIGHT, height_slice))
        self.clear_occupied_candidates()
        self.clear_duplicate_candidates()

    def clear_occupied_candidates(self):
        clear_idx = []
        for idx, candidate in enumerate(self.candidates_points):
            if self.envelope_space[candidate[0],candidate[1],candidate[2]] == 1:
                clear_idx.append(idx)
        idx_offset = 0
        for idx in clear_idx:
            self.candidates_points.pop(idx - idx_offset)
            idx_offset += 1              

    def clear_duplicate_candidates(self):
        candidates = []
        for idx, candidate in enumerate(self.candidates_points):
            already_in = False
            for in_candidate in candidates:
                if candidate[0] == in_candidate[0] and \
                   candidate[1] == in_candidate[1] and \
                   candidate[2] == in_candidate[2]:
                       already_in = True
                       break
            if not already_in:
                candidates.append(candidate)
        self.candidates_points = candidates

    def update_history(self, new_bin:Bin, result:Tuple[int,int,int]):
        self.search_history.append((new_bin.size_list, result))
    
    def brute_find_part(self, 
                        new_bin:Bin, 
                        axises_rotate:Tuple[Axis, Axis, Axis], 
                        axises:Tuple[Axis, Axis, Axis], 
                        start_point:Tuple[int,int,int]=(0,0,0), 
                        strict_level:int=3) -> Tuple[int,int,int]:
        if self.search_history != [] and new_bin.size_list == self.search_history[-1][0]:
            if self.search_history[-1][1] == None:
                return None
        if not self.volumn_check(new_bin):
            return None
        new_bin.axis_sort(axises_rotate)
        if not utils.axis_utils.valid_axis(axises):
            raise ValueError("Axises are not valid!")
        search_axis = utils.axis_utils.lwh_to_axis(self.size_list, axises)
        axis_start_point = utils.axis_utils.lwh_to_axis(start_point, axises)
        axis_space = np.transpose(self.space, (utils.axis_utils.lwh_to_axis_map(axises)))
        bin_axis = utils.axis_utils.lwh_to_axis(new_bin.size_list, axises)
        
        skip_axis = [False, False, False]
        for axis_0 in range(0, search_axis[0] - bin_axis[0] + 1):
            if axis_0 < axis_start_point[0]:
                continue
            if search_axis[1]*search_axis[2] - np.sum(axis_space[axis_0]) < bin_axis[1] * bin_axis[2]:
                continue
            for axis_1 in range(0, search_axis[1] - bin_axis[1] + 1):
                if axis_0 == axis_start_point[0] and axis_1 < axis_start_point[1]:
                    continue
                if search_axis[2] - np.sum(axis_space[axis_0, axis_1]) < bin_axis[2]:
                    continue
                for axis_2 in range(0, search_axis[2] - bin_axis[2] + 1):
                    if axis_0 == axis_start_point[0] and axis_1 == axis_start_point[1] and axis_2 < axis_start_point[2]:
                        continue
                    if axis_space[axis_0, axis_1, axis_2] == 1:
                        continue
                    axis_index_list = [axis_0, axis_1, axis_2]
                    idx_length, idx_width, idx_height = utils.axis_utils.axis_to_lwh(axis_index_list, axises)
                    results = self.put(new_bin, (idx_length, idx_width, idx_height), strict_level)
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
    def brute_find_with_heuristics(self, 
                                   new_bin:Bin, 
                                   axises_rotate:Tuple[Axis, Axis, Axis], 
                                   axises:Tuple[Axis, Axis, Axis], 
                                   try_rotate:bool=True, 
                                   strict_level:int=3) -> Tuple[int, int, int]:
        if self.search_history != [] and new_bin.size_list == self.search_history[-1][0]:
            if self.search_history[-1][1] == None:
                return None
        if not self.volumn_check(new_bin):
            return None
        new_bin.axis_sort(axises_rotate)
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
            bin_location = self.brute_find_part(new_bin, axises_rotate, axises, strict_level=strict_level)
        else:
            suit_one = False
            for idx_point,next_position in enumerate(next_points):
                suit = False
                if try_rotate:
                    for idx_axis, axis_type in enumerate(utils.axis_utils.full_axis_type()):
                        copy_bin = Bin(new_bin.l, new_bin.w, new_bin.h, self.precision)
                        copy_bin.axis_transform(axis_type)
                        results = self.put(copy_bin, next_position, strict_level)
                        if all(results):
                            if idx_axis != 0:
                                logger.info(f"Rotate bin to {axis_type}")
                            bin_location = next_position
                            suit = True
                            break
                else:
                    results = self.put(new_bin, next_position, strict_level)
                    if all(results):
                        bin_location = next_position
                        suit = True
                if suit:
                    suit_one = True
                    break
            if not suit_one:
                bin_location = self.brute_find_part(new_bin, axises_rotate, axises, strict_level=strict_level)
        if bin_location != None:
            self.add_next_points(bin_location, new_bin)
        return bin_location

    def sub_space_find(self, 
                       new_bin:Bin, 
                       axises_rotate:Tuple[Axis, Axis, Axis], 
                       axises:Tuple[Axis, Axis, Axis], 
                       strict_level:int=3) -> Tuple[int, int, int]:
        if self.search_history != [] and new_bin.size_list == self.search_history[-1][0]:
            if self.search_history[-1][1] == None:
                return None
        if not self.volumn_check(new_bin):
            return None
        new_bin.axis_sort(axises_rotate)
        if self.candidates_points == []:
            self.candidates_points = [(0,0,0)]
        # sorted_bin = sorted((new_bin.length, new_bin.width, new_bin.height))
        candidates_match_ratio = []
        for idx, candidate_start in enumerate(self.candidates_points):
            # candidate_space = (self.max_length - candidate_start[0],
            #                    self.max_width - candidate_start[1],
            #                    self.max_height - candidate_start[2])
            # sorted_space = sorted(candidate_space)
            # raw_match = [sorted_space[0] / sorted_bin[0], sorted_space[1] / sorted_bin[1], sorted_space[2] / sorted_bin[2]]
            # mean_match = sum(raw_match) / len(raw_match)
            # raw_match = [x - mean_match for x in raw_match]
            # raw_match = [x / mean_match for x in raw_match]
            # raw_match = [abs(x) for x in raw_match]
            candidate_match_ratio = -sum(candidate_start)
            candidates_match_ratio.append(candidate_match_ratio)
        candidates = list(zip(list(range(len(self.candidates_points))), 
                              self.candidates_points, 
                              candidates_match_ratio))
        candidates = sorted(candidates, key=lambda x: x[2], reverse=True)
        for candidate in candidates:
            pick_idx = candidate[0]
            pick_candidate_point = candidate[1]
            # axis_sort = utils.axis_utils.lwh_sort(self.size_list)
            # new_bin.axis_sort(axis_sort)   
            results = self.put(new_bin, pick_candidate_point, strict_level)
            if all(results):
                self.add_candidates(pick_candidate_point, new_bin)
                return pick_candidate_point
            else:
                continue
        bin_location = self.brute_find_part(new_bin, axises_rotate, axises, strict_level=strict_level)
        if bin_location != None:
            self.add_candidates(bin_location, new_bin)
        return bin_location

    def greedy_search(self, 
                      new_bin:Bin, 
                      axises_rotate:Tuple[Axis, Axis, Axis], 
                      axises:Tuple[Axis, Axis, Axis], 
                      strict_level:int=3) -> Tuple[int, int, int]: 
        if self.search_history != [] and new_bin.size_list == self.search_history[-1][0]:
            if self.search_history[-1][1] == None:
                return None
        if not self.volumn_check(new_bin):
            return None
        new_bin.axis_sort(axises_rotate)
        for width_idx in range(self.max_width - new_bin.width + 1):
            for length_idx in range(self.max_length - new_bin.length + 1):
                bin_projection = self.simple_space[length_idx:length_idx+new_bin.length, 
                                                    width_idx:width_idx+new_bin.width]
                current_height = np.max(bin_projection)
                if (self.max_height - current_height >= new_bin.height):
                    result = self.put(new_bin, (length_idx, width_idx, current_height), strict_level)
                    if all(result):
                        return (length_idx, width_idx, current_height)
        
        bin_location = self.brute_find_part(new_bin, axises_rotate, axises, strict_level=strict_level)
        return bin_location
                    
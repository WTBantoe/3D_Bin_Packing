from Common import *
import argparse

def to_axis(char):
    assert len(char) == 1, Axis.UnknownAxis
    if char == "l":
        return Axis.LENGTH
    elif char == "w":
        return Axis.WIDTH
    elif char == "h":
        return Axis.HEIGHT

def to_method(method):
    if method == "brute":
        return SearchMethod.BRUTE
    elif method == "greedy":
        return SearchMethod.GREEDY
    elif method == "candidate_point":
        return SearchMethod.CANDIDATE_POINTS
    elif method == "sub_space":
        return SearchMethod.SUB_SPACE
    else:
        raise SearchMethod.UnknownSearchMethod

def get_args():
    # parse_known_args()
    task_parser = argparse.ArgumentParser()
    task_parser.add_argument("--bin_types", type=int, required=True, choices=[3,5,8,10,15])
    task_parser.add_argument("--test_index", type=int, required=False, default=0, choices=[0,1,2,3,4,5])
    task_parser.add_argument("--strict_level", type=int, required=False ,default=3, choices=[0,1,2,3])  
    task_args, remain_args = task_parser.parse_known_args()

    type_parser = argparse.ArgumentParser()
    type_parser.add_argument("--type", required=True, choices=["online", "offline"])
    type_args, remain_args = type_parser.parse_known_args(remain_args)
    
    method_parser = argparse.ArgumentParser()

    if type_args.type == "online":
        method_parser.add_argument("--method", type=to_method, required=True, choices=[SearchMethod.BRUTE,SearchMethod.GREEDY,SearchMethod.CANDIDATE_POINTS,SearchMethod.SUB_SPACE])
        method_args, remain_args = method_parser.parse_known_args(remain_args)
        
        config_parser = argparse.ArgumentParser()
        config_parser.add_argument("--bin_rotate", nargs=3, type=to_axis, required=False, default=[Axis.LENGTH,Axis.WIDTH,Axis.HEIGHT])
        if method_args.method == SearchMethod.BRUTE:  # 暴力搜索 
            config_parser.add_argument("--axises", nargs=3, type=to_axis, required=False, default=[Axis.LENGTH,Axis.WIDTH,Axis.HEIGHT])
            config_args = config_parser.parse_args(remain_args)
        elif method_args.method == SearchMethod.GREEDY: # 贪心算法
            config_parser.add_argument("--axises", nargs=2, type=to_axis, required=False, default=[Axis.LENGTH,Axis.WIDTH])
            config_args = config_parser.parse_args(remain_args)
        elif method_args.method == SearchMethod.CANDIDATE_POINTS: # 候选点搜索
            config_parser.add_argument("--try_rotate", action="store_true")
            config_args = config_parser.parse_args(remain_args) 
    elif type_args.type == "offline":
        method_parser.add_argument("--method", type=to_method, required=True, choices=["brute","greedy","candidate_point","sub_space"])
        method_args, remain_args = method_parser.parse_known_args(remain_args)
        config_args = None

    return task_args, type_args, method_args, config_args





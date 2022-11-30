from random import random
from typing import List

from Bin import Bin
from Container import Container


def generate_bins(bin_num:int, container:Container) -> List[Bin]:
    bin_list = []
    for idx in range(bin_num):
        l = container.ml * random() / 4 + 10 ** (-container.precision)
        h = container.mh * random() / 4 + 10 ** (-container.precision)
        w = container.mw * random() / 4 + 10 ** (-container.precision)
        new_bin = Bin(l, h, w, container.precision)
        bin_list.append(new_bin)
    return bin_list
    
    
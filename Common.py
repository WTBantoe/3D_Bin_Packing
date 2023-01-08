import os
import random
from enum import Enum

random.seed(1)

class Axis(Enum):
    LENGTH = 0
    WIDTH = 1
    HEIGHT = 2

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    class UnknownAxis(Exception):
        def __init__(self):
            super().__init__()

    class InvalidAxis(Exception):
        def __init__(self):
            super().__init__()

class SearchMethod(Enum):
    NONE = 0
    BRUTE = 1
    GREEDY = 2
    CANDIDATE_POINTS = 3
    SUB_SPACE = 4

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    class UnknownSearchMethod(Exception):
        def __init__(self):
            super().__init__()

PRECISION = 0 # =10^x

LOG_DIR = os.path.abspath(os.path.join(os.path.split(os.path.realpath(__file__))[0],"./Logs"))
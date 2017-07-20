#!/usr/bin/env python3
from agent import *
from piece import *
from core import *
import random
from envy_free_allocation import *
from copy import copy
from time import time

if __name__ == '__main__':
    set_debug(True)

    #seed =  1499115613878
    #seed = 1499456800813
    #seed = 1499898496367

    #This seed produces the "golden output"
    #seed = 1500335285296

    #These seeds break strategy choose_by_above_trims for 12 players
    #seed = 1500531379583
    seed = 1500534838022

    random.seed(seed)
    agents = [Agent(division_count=random.randint(10,20)) for i in range(12)]
    core_number = get_envy_free_allocation(agents, Piece.get_whole_piece())

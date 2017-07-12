#!/usr/bin/env python3
import unittest
from agent import *
from piece import *
from random import *
from core import *
from time import sleep
from waste_makes_haste import *
from debug import *

class WasteMakesHasteTests(unittest.TestCase):
    
    def test_P(self):
        self.assertEqual(
                [P(i) for i in range(0,12)],
                [1,2,3,5,9,17,33,65,129,257,513,1025]
                )

    def test_preference_random(self):
        for n in range(2,6):
            #set_debug(True)
            print(n)
            for t in range(20):
                agents = [Agent(randint(5,23)) for i in range(n)]
                pieces = get_waste_makes_haste_allocation(agents, Piece.get_whole_piece())
                self.assertTrue(envy_free(pieces))

def main():
    unittest.main()

if __name__ == '__main__':
    main()

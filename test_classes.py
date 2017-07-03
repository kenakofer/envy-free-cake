#!/usr/bin/env python3
import unittest
from agent import *
from piece import *
import random
from core import *
from debug import *
from copy import copy
from time import time
from envy_free_allocation import *

class AgentTests(unittest.TestCase):
    def test_goes_to_1(self):
        for i in range(100):
            a = Agent()
            v = a.get_value(Piece.get_whole_piece())
            self.assertTrue( v == 1 )

    def test_trim_value1(self):
        test_values = list(map(Fraction, [0,1])) + [Fraction(random.random()) for i in range(10)]
        for v in test_values:
            a = Agent()
            p = Piece.get_whole_piece()
            assert type(v) == Fraction
            t = a.get_trim_of_value(p, v)
            p.trims.append(t)
            self.assertTrue(a.get_value(p) == v)
        
    def test_trim_value2(self):
        test_pieces = []
        test_count=20
        i_num = 10
        for j in range(test_count):
            test_pieces.append(get_random_piece(i_num))

        for p in test_pieces:
            #print("Piece has intervals",p.intervals)
            a = Agent()
            v = Fraction(random.random()) * a.get_value(p)
            t = a.get_trim_of_value(p, v)
            p.trims.append(t)
            #print('v:',float(v))
            #print('  ',float(a.get_value(p)))
            self.assertTrue(a.get_value(p) == v)

    def test_n_split(self):
        for n in range(2,20):
            a = Agent()
            #a = Agent(division_count=1, preference_function=lambda x: 1)
            assert len(a.cached_values) == 0
            piece = get_random_piece(10)
            total_value = a.get_value(piece)
            pieces = a.cut_into_n_pieces_of_equal_value(n, piece)
            for p in pieces:
                self.assertTrue(a.get_value(p, count=False) == Fraction(total_value, n))
                self.assertTrue(pieces.count(p) == 1)
            #Testing the counts
            self.assertTrue(a.trim_count == n-1)

    def test_save_agent_preferences(self):
        for i in range(200):
            p = get_random_piece(random.randint(1,20))
            a = Agent()
            pref_string = a.get_preference_string()
            first_value = a.get_value(p)
            a2 = Agent()
            a2.set_preferences(pref_string)
            assert a2.get_preference_string() == pref_string
            assert a2.get_value(p) == first_value

    def test_preference_fractalization(self):
        for n in range(4,6):
            agents = [Agent(random.randint(5,23)) for i in range(n)]
            pieces = core(agents[0], agents, Piece.get_whole_piece())
            residue = Piece.extract_residue_from_pieces(pieces)
            if not Piece.is_empty(residue):
                for a in agents:
                    residue_value_before = a.get_value(residue)
                    old_adv = copy(a.adv)
                    self.assertEqual(a.value_up_to(Fraction(1)), 1)
                    a.fractalize_preferences(residue.intervals)
                    assert a.adv != old_adv
                    self.assertEqual(a.value_up_to(Fraction(1)), 1)

    def test_fractalization_correctness(self):
        for n in range(4,6):
            agents = [Agent(random.randint(5,23)) for i in range(n)]
            pieces = core(agents[0], agents, Piece.get_whole_piece())
            residue = Piece.extract_residue_from_pieces(pieces)
            if not Piece.is_empty(residue):
                for a in agents:
                    residue_value_before = a.get_value(residue)
                    old_adv = copy(a.adv)
                    self.assertEqual(a.value_up_to(Fraction(1)), 1)
                    a.fractalize_preferences(residue.intervals)
                    assert a.adv != old_adv
                    self.assertEqual(a.value_up_to(Fraction(1)), 1)
                #Run core again and make sure pieces are the same
                #Clear caches of agents
                for a in agents:
                    a.cached_values={}
                new_pieces = core(agents[0], agents, Piece.get_whole_piece())
                self.assertEqual( [(p.hash_info(), p.allocated) for p in new_pieces], [(p.hash_info(), p.allocated) for p in pieces] )

    def test_random_seeding(self):
        seed = int(time()*1000)
        random.seed(seed)
        agents1 = [Agent() for i in range(6)]
        pieces1 = get_envy_free_allocation(agents1, Piece.get_whole_piece())
        random.seed(seed)
        agents2 = [Agent() for i in range(6)]
        pieces2 = get_envy_free_allocation(agents2, Piece.get_whole_piece())
        self.assertEqual([p.hash_info() for p in pieces1], [p.hash_info() for p in pieces2])
    
    def test_choose_ranking(self):
        for n in [5]*10:
            a = Agent()
            piece = get_random_piece(10)
            pieces = a.cut_into_n_pieces_of_equal_value(n, piece)
            ranking_order = pieces[:]
            random.shuffle(ranking_order)
            random.shuffle(pieces)
            a.ranking = ranking_order[:]
            self.assertEqual(a.choose_piece(pieces), a.ranking[0])



def get_random_piece(interval_count):
    nums =  sorted([Fraction(random.random()) for i in range(interval_count*2)])
    intervals = []
    for i in range(0,interval_count*2,2):
        intervals.append(Interval(nums[i], nums[i+1]))
    return Piece(intervals)

    

      


def main():
    unittest.main()

if __name__ == '__main__':
    main()

import unittest
from classes import *
from random import *

class AgentTests(unittest.TestCase):

    def test_goes_to_1(self):
        for i in range(100):
            a = Agent()
            cake = Cake()
            v = a.get_value(cake.pieces[0])
            self.assertTrue( v == 1 )

    def test_trim_value1(self):
        test_values = list(map(Fraction, [0,1])) + [Fraction(random()) for i in range(10)]
        for v in test_values:
            a = Agent()
            cake = Cake()
            p = cake.pieces[0]
            t = a.get_trim_of_value(p, v)
            p.trims.append(t)
            #print('v:',float(v))
            #print('  ',float(a.get_value(p)))
            self.assertTrue(a.get_value(p) == v)
        
    def test_trim_value2(self):
        cake = Cake()

        test_pieces = []
        test_count=50
        i_num = 10
        for j in range(test_count):
            test_pieces.append(self.get_random_piece(cake, i_num))

        for p in test_pieces:
            #print("Piece has intervals",p.intervals)
            a = Agent()
            v = Fraction(random()) * a.get_value(p)
            t = a.get_trim_of_value(p, v)
            p.trims.append(t)
            #print('v:',float(v))
            #print('  ',float(a.get_value(p)))
            self.assertTrue(a.get_value(p) == v)

    def test_n_split(self):
        for n in range(1,20):
            #print(n)
            cake = Cake()
            a = Agent()
            piece = self.get_random_piece(cake, randint(1,50))
            total_value = a.get_value(piece)
            pieces = a.cut_into_n_pieces_of_equal_value(n, piece)
            for p in pieces:
                self.assertTrue(a.get_value(p) == Fraction(total_value, n))
                self.assertTrue(pieces.count(p) == 1)

    def get_random_piece(self, cake, interval_count):
        nums =  sorted([Fraction(random()) for i in range(interval_count*2)])
        intervals = []
        for i in range(0,interval_count*2,2):
            intervals.append(Interval(nums[i], nums[i+1]))
        return Piece(cake, intervals)
            


def main():
    unittest.main()

if __name__ == '__main__':
    main()

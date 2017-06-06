import unittest
from classes import *
from random import *
from core import *

class AgentTests(unittest.TestCase):

    def test_core(self):
        for i in range(50):
            for n in [3]:
                print()
                print('Testing core on',n,'agents')
                agents = [Agent() for i in range(n)]
                cake = Cake()
                pieces = core(agents[0], agents, cake.pieces[0])
                self.assertTrue( True )

def main():
    unittest.main()

if __name__ == '__main__':
    main()

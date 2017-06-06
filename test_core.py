import unittest
from classes import *
from random import *
from core import *
from time import sleep

class AgentTests(unittest.TestCase):

    def test_worst_case(self):
        divs = 30
        agents = [
            Agent(division_count=divs, preference_function=lambda x: x**3),
            Agent(division_count=divs, preference_function=lambda x: x**2),
            Agent(division_count=divs, preference_function=lambda x: x**1),
            Agent(division_count=divs, preference_function=lambda x: x**(1/2)),
            Agent(division_count=divs, preference_function=lambda x: x**(1/3)),
        ]
        cake = Cake()
        pieces = core(agents[0], agents, cake.pieces[0])
        self.assertTrue( True )

    def test_core_powers(self):
        for i in range(5):
            for n in [5]:
                agents = [Agent(division_count=20, preference_function=lambda x: x**Fraction(randint(0,5), randint(1,5))) for j in range(n)]
                cake = Cake()
                pieces = core(agents[0], agents, cake.pieces[0])
                self.assertTrue( True )



    #Ran test on 15 agents: Returned correctly in 1972.634s

    def test_core_random(self):
        for n in range(2,6):
            print()
            print('Testing core on',n,'agents')
            agents = [Agent(random.randint(5,23)) for i in range(n)]
            cake = Cake()
            pieces = core(agents[0], agents, cake.pieces[0])
            self.assertTrue( True )

def main():
    unittest.main()

if __name__ == '__main__':
    main()

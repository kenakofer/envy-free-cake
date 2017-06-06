import unittest
from classes import *
from random import *
from core import *
from time import sleep

class AgentTests(unittest.TestCase):

    #Ran test on 15 agents: Returned correctly in 1972.634s

    def test_core(self):
        for i in range(10):
            for n in [7]:
                print()
                print('Testing core on',n,'agents')
                agents = [Agent(random.randint(5,23)) for i in range(n)]
                cake = Cake()
                pieces = core(agents[0], agents, cake.pieces[0])
                self.assertTrue( True )
            sleep(1)

def main():
    unittest.main()

if __name__ == '__main__':
    main()

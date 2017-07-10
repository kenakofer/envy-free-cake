from agent import *
from piece import *

def get_waste_makes_haste_allocation(agents, pieces, fractalize=True):
    for i, agent in enumerate(agents):
        agent.trimmed_pieces = equalize(agent, pieces, P(len(agents)-i-1))
    for i in range(len(agents)-1, -1, -1):
        agent = agents[i]
        trimmed_choose_from = [p for p in pieces if p.allocated==None and p in agent.trimmed_pieces]
        if len(trimmed_choose_from) > 0:
            choice = agent.choose_piece(trimmed_choose_from)
        else:
            choice = agent.choose_piece(pieces)
            assert choice.allocated == None
        choice.allocated = agent
    return pieces

def equalize(agent, pieces, k):
    #TODO

'''
select_l_star algorithm is modeled off of Algorithm 3 (pg 20) in
Efficient Algorithms for Envy-Free Stick Division With Fewest Cuts
Raphael Reitzig and Sebastian Wild, April 13, 2015
https://arxiv.org/pdf/1502.04048.pdf
'''
def select_l_star(L, k):
    #TODO

def P(k):
    return 2**(k-1) + 1

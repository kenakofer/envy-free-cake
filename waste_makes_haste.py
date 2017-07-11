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
    n = len(L)
    ## 1
    np = min(k, n+1)
    ## 2
    if np <= n:
        ## 2.1 Determine L_co := L(n'), i. e. the n'th largest length
        L_co = sorted(L, reverse=True)[np-1]
        ## 2.2. If L_co is optimal, answer l* = L_co (and terminate).
        if is_optimal(L, k, L_co):
            return L_co
    ## 2' so np > n
    else:
        ## 2.4
        L_co = 0
    ## 3 Assemble I_co = I_>L_co
    ## pg 14: We will restrict ourselves for the remainder of this 
    ## article to index sets I_co that contain indices of lengths that 
    ## are larger than the n'th largest length L(n') in L
    I_co = [i for i,stick in enumerate(L) if stick > L_co]
    ## 4 Compute C := C(I_co, f_l, f_u) as multiset.
    ## pg 13 gives definition of candidate multiset


'''
(pg 17), step 2.2 in the algorithm proof
'''
def is_optimal(L, k, l):
    a, m_L = m(L, l)
    return k <= m_L < k+a 

'''
The number of pieces of length l that we can get by cutting the set 
of sticks L into sticks no longer than l. (pg 9) The computation of
a is added as per step 2.2 on pg 17
'''
def m(L, length):
    a = 0
    m = 0
    for stick in L:
        m += stick // length
        if stick % length == 0:
            a+=1
    return a, m

def P(k):
    return 2**(k-1) + 1

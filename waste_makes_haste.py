from agent import *
from piece import *
from fractions import Fraction
from debug import debug_print

def get_waste_makes_haste_allocation(agents, pieces):
    if type(pieces) == Piece:
        pieces = [pieces]
    for i, agent in enumerate(agents):
        agent.trimmed_pieces = equalize(agent, pieces, P(len(agents)-i-1))
    for agent in agents[::-1]:
        trimmed_choose_from = [p for p in pieces if p.allocated==None and p in agent.trimmed_pieces]
        if len(trimmed_choose_from) > 0:
            choice = agent.choose_piece(trimmed_choose_from)
        else:
            choice = agent.choose_piece(pieces)
            assert choice.allocated == None
        choice.allocated = agent
    return pieces

def P(k):
    if k <= 0:
        # The last agent does not need to trim anything
        return 1
    else:
        return 2**(k-1) + 1

def equalize(agent, pieces, k):
    debug_print(agent,"is equalizing",k)
    values = list(map(agent.get_value, pieces))
    value_to_cut = select_l_star(values, k)
    trimmed_pieces = []
    for p in pieces[:]:
        p_original = p
        pieces.remove(p)
        while agent.get_value(p) > value_to_cut:
            t = agent.get_trim_of_value(p, value_to_cut)
            p.trims = [t]
            p, right_piece = p.split_at_rightmost_trim()
            pieces.append(right_piece)
            trimmed_pieces.append(right_piece)
        pieces.append(p)
        # Should I add the leftover piece?
        #if p != p_original and agent.get_value(p) == value_to_cut:
        #    trimmed_pieces.append(p)
    # Assert that equalize accomplished its task:
    count=0
    for p in pieces:
        assert agent.get_value(p) <= value_to_cut
        if agent.get_value(p) == value_to_cut:
            count += 1
    assert count >= k
    # This method modified the pieces list in place, only return the trimmed_pieces
    return trimmed_pieces

'''
select_l_star algorithm is modeled off of Algorithm 2 (pg 16) in
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
    ## I belive that we can use f_l = 1 and f_u = k as per Lemma 2.8 (pg 15)
    f_l = 1; f_u = k
    C = set(Fraction(L[i], j) for j in range(f_l,f_u+1) for i in I_co if f_l <= j <= f_u)
    C = sorted(list(C))
    
    ## 5 Find l* by binary search on C w.r.t. Feasible
    ## I believe they mean specifically to find the last value in C which is Feasible.
    while True:
        if len(C) == 1:
            break
        mid = len(C) // 2
        if is_feasible(L, k, C[mid]):
            C = C[mid:]
        else:
            C = C[:mid]

    ## 6 Answer l*
    return C[0]



'''
(pg 17), step 2.2 in the algorithm proof
'''
def is_optimal(L, k, l):
    a, m_L = m(L, l, return_a=True)
    return k <= m_L < k+a 

'''
The number of pieces of length l that we can get by cutting the set 
of sticks L into sticks no longer than l. (pg 9) The computation of
a is added as per step 2.2 on pg 17
'''
def m(L, length, return_a=False):
    a = 0
    m = 0
    for stick in L:
        m += stick // length
        if stick % length == 0:
            a+=1
    if return_a:
        return a, m 
    else:
        return m

'''
(pg 10)
'''
def is_feasible(L,k,l):
    return m(L,l) >= k


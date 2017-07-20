#!/usr/bin/env python3
from agent import *
from piece import *
from core import *
from debug import *
from waste_makes_haste import *
from time import time

def get_envy_free_allocation(agents, piece, get_call_number=False, fractalize=True):
    Piece.piece_counter = 0
    Agent.agent_counter = 0
    agents = agents[:]
    for a in agents:
        a.value_count = 0
        a.trim_count = 0
        a.cached_values = {}
    #We will be updating each agent's allocated cake throughout the algorithm
    allocated_cake = [a.allocated_cake for a in agents]
    residue = piece
    for i in range(100):
        debug_print(' ',i,' Agent count:',len(agents))
        cutter = agents[ i % len(agents) ]
        other_agents = [a for a in agents if a != cutter]

        #Run core and get the updated residue
        pieces = core(cutter, agents, residue)
        residue = Piece.extract_residue_from_pieces(pieces)

        ### add to player's allocations
        for p in pieces:
            p.allocated.allocated_cake += p

        # Check if residue is None. If so, return envy free allocation! Also return if the residue is full of empty intervals
        if Piece.is_empty(residue):
            return i+1 if get_call_number else allocated_cake

        # See if we can reduce the number of players using a dominating set
        dominating_set = Agent.get_dominating_set(agents, allocated_cake, residue)
        if dominating_set != None:
            dominated = list(dominating_set[1])
            agents = dominated

        #Fractalize the player preferences
        if fractalize:
            for a in agents:
                a.fractalize_preferences(residue.intervals)

def get_waste_makes_haste_envy_free_allocation(agents, piece, get_call_number=False, fractalize=True):
    Piece.piece_counter = 0
    Agent.agent_counter = 0
    agents = agents[:]
    for a in agents:
        a.value_count = 0
        a.trim_count = 0
        a.cached_values = {}
    #We will be updating each agent's allocated cake throughout the algorithm
    allocated_cake = [a.allocated_cake for a in agents]
    residue = piece
    for i in range(100):
        debug_print(' ',i,' Agent count:',len(agents))

        #Run core and get the updated residue
        pieces = get_waste_makes_haste_allocation(agents, residue)
        residue = sum([p for p in pieces if p.allocated==None], Piece([]))

        ### add to player's allocations
        for p in pieces:
            if p.allocated != None:
                p.allocated.allocated_cake += p

        # Check if residue is None. If so, return envy free allocation! Also return if the residue is full of empty intervals
        if Piece.is_empty(residue):
            assert envy_free(allocated_cake)
            return i+1 if get_call_number else allocated_cake

        # See if we can reduce the number of players using a dominating set
        dominating_set = Agent.get_dominating_set(agents, allocated_cake, residue)
        if dominating_set != None:
            dominated = list(dominating_set[1])
            agents = dominated

        #Fractalize the player preferences
        if fractalize:
            for a in agents:
                a.fractalize_preferences(residue.intervals)

if __name__ == '__main__':
    for n in range(3,7):
        print()
        print('For',n,'agents:')
        for i in range(6):
            agents = [Agent() for j in range(n)]

            start_time = time()
            calls = get_waste_makes_haste_envy_free_allocation(agents, Piece.get_whole_piece(), get_call_number=True)
            total_time = time() - start_time
            trims = sum([a.trim_count for a in agents])
            values = sum([a.value_count for a in agents])
            
            print('Waste makes haste: calls/values/trims/time:', calls, values, trims, total_time)
            
            start_time = time()
            calls = get_envy_free_allocation(agents, Piece.get_whole_piece(), get_call_number=True)
            total_time = time() - start_time
            trims = sum([a.trim_count for a in agents])
            values = sum([a.value_count for a in agents])
            print('Core: calls/values/trims/time:             ', calls, values, trims, total_time)

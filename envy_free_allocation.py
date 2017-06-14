from classes import *
from core import *
from debug import *

def get_envy_free_allocation(agents, piece):
    for a in agents:
        a.allocated_piece = Piece([])
        a.allocated_piece.allocated = a

    allocated_pieces = [a.allocated_piece for a in agents]
    residue = piece
    for i in range(100):
        print(' ',i,' Agent count:',len(agents))
        cutter = agents[ i % len(agents) ]
        other_agents = [a for a in agents if a != cutter]

        #Run core and get the updated residue
        pieces = core(cutter, agents, residue)
        residue = Piece.extract_residue_from_pieces(pieces)

        ### add to player's allocations
        for p in pieces:
            p.allocated.allocated_piece += p

        # Check if residue is empty. If so, return envy free allocation!
        empty = True
        for i in residue.intervals:
            if i.left != i.right:
                empty = False
                break
        if empty:
            return allocated_pieces

        dominating_set = Agent.get_dominating_set(agents, allocated_pieces, residue)
        if dominating_set != None:
            dominated = list(dominating_set[1])
            agents = dominated

if __name__ == '__main__':
    for i in range(10):
        print()
        print(i)
        agents = [Agent() for i in range(8)]
        pieces = get_envy_free_allocation(agents, Piece.get_whole_piece())

        for p in pieces:
            print(p.hash_info())

        assert envy_free(pieces)

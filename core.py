from classes import *
from subcore import *
from debug import *

def core(agent_to_cut, agents, piece):
    assert agent_to_cut in agents
    pieces = agent_to_cut.cut_into_n_pieces_of_equal_value(len(agents), piece)
    for a in agents:
        a.benchmark = 0
    subcore(pieces, [a for a in agents if a != agent_to_cut])
    unallocated_pieces = [p for p in pieces if p.allocated == None]
    assert len(unallocated_pieces) == 1
    unallocated_pieces[0].allocated = agent_to_cut
    assert envy_free(pieces)
    return pieces

from agent import *
from piece import *
from subcore import *
from debug import *

'''''''''
Returns an envy-free partial allocation of the piece passed in

Comment styles:
## Comments:   Code from Aziz and Mackenzie's algorithm
# Comments:    Disabled code
Triple quotes: Implementation commentary
'''''''''

def core(agent_to_cut, agents, piece):
    assert agent_to_cut in agents

    ## 1: Ask agent i to cut the cake R into n equally preferred pieces
    pieces = agent_to_cut.cut_into_n_pieces_of_equal_value(len(agents), piece)

    ## 2: Run SubCore Protocol on the n pieces with agents set N \ {i} with each agent having a benchmark value as zero.
    for a in agents:
        a.benchmark = 0
    subcore(pieces, [a for a in agents if a != agent_to_cut])

    ## 3: Give i one of the unallocated untrimmed pieces from the previous step
    unallocated_pieces = [p for p in pieces if p.allocated == None]
    assert len(unallocated_pieces) == 1
    unallocated_pieces[0].allocated = agent_to_cut
    
    ## 4: Return an envy-free partial allocation as well as the unallocated cake
    ''' Leave commented to avoid caching values that will mess up value_counts '''
    #assert envy_free(pieces)
    ''' 
    Note that our implementation returns pieces with trims placed on them 
    to indicate where the residue should be cut off
    '''
    return pieces

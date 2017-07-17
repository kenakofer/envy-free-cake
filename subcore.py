from agent import *
from piece import *
from debug import *

'''''''''
Returns a neat, partial, envy-free alocation of pieces of cake among the agents given

Comment styles:
## Comments:   Code from Aziz and Mackenzie's algorithm
# Comments:    Disabled code
Triple quotes: Implementation commentary

'''''''''
def subcore(pieces, agents, above_ranking=None, call_signature="top"):
    set_debug_prefix(call_signature)
    debug_print()
    debug_print(call_signature)
    debug_print("Calling subcore with",len(pieces),"pieces and",len(agents),'agents')

    ''' It's a bin for trims! (storing trims made in this call of subcore :) '''
    trim_bin = [] 

    ## 1: Set value a_j to the value of agent j's most preferred piece
    '''
    We don't do this, in order to minimize the number of queries needed later on. When such values are
    needed for the first time, they will be computed
    '''

    ## 2: Order agents lexicographically
    agents.sort(key=lambda a: a.number)
    pieces.sort(key=lambda p: p.number)

    ## 3: Ask each agent to rank the pieces
    current_ranking = {}
    for a in agents:
        current_ranking[a] = a.get_ranking(pieces, above_ranking)
        debug_print(a,'has current_ranking',current_ranking[a])

    ''' Ensure that no piece passed in was trimmed by an agent passed in '''
    for p in pieces:
        for t in p.trims:
            assert t.owner not in agents

    for p in pieces:
        assert p.allocated == None

    ## 4: FOR m=1 to the size of agents do:
    for m in range(1,len(agents)+1):
        debug_print("m=",m)

        debug_print(agents[m-1],'is choosing a piece. Their current_ranking:')
        debug_print('',current_ranking[agents[m-1]])
        debug_print('Their options:')
        for p in pieces:
            debug_print('',p, float(agents[m-1].get_value(p, count=False)))

        ## 5: IF there is an unallocated piece which gives the agent the highest value among all the pieces:
        preferred_piece = agents[m-1].choose_piece(pieces, current_ranking=current_ranking)
        debug_print('They chose',preferred_piece)

        if preferred_piece.allocated == None:
            ## 6: Tentatively give the piece to the agent, and proceed to the next iteration of the FOR loop
            preferred_piece.allocated = agents[m-1]
        ## ELSE
        else:
            ## 7a: The first m agents are contesting for the same m-1 pieces, called the contested pieces
            contested_pieces = list(filter(lambda p: p.allocated != None, pieces))
            uncontested_pieces = list(filter(lambda p: p.allocated == None, pieces))
            assert len(uncontested_pieces) >= 1

            ## 7b: Each agent in m is asked to place a trim on each contested piece so that the cake right of the trim is
            ## equal in value to the agent's preferred uncontested piece.
            for agent in agents[:m]:
                uncontested_max_value = max( [agent.get_value(p) for p in uncontested_pieces] )
                debug_print(agent, "uncontested max value is",float(uncontested_max_value))
                for piece in contested_pieces:
                    '''
                    Because new valuations are made from the rightmost trim, don't immediately
                    add these new trims to the piece.
                    '''
                    possible_trim = agent.get_trim_of_value(piece, uncontested_max_value)
                    debug_print(agent,'trimmed',piece,'with result',possible_trim) 
                    if possible_trim != None:
                        trim_bin.append(possible_trim)
                        possible_trim.signature = call_signature
                        piece.pending_trims.append(possible_trim)
            ''' Now add the pending trims to the actual trims '''
            for piece in contested_pieces:
                piece.trims.extend(piece.pending_trims)
                ''' Make sure the trims are sorted by their x position '''
                piece.trims.sort( key = lambda t: t.x )
                piece.pending_trims = []

            ## 7c: Update agent benchmarks
            '''
            We don't see benchmarks as even necessary, because
            they don't modify the flow of code at all. But they're used in the proof...
            '''
            #for agent in agents:
            #    agent.benchmark = max( [agent.get_value(p) for p in uncontested_pieces] )

            ## 8: Set W to be the set of agents who trimmed the most on any contested piece
            ## If multiple agents trim the most on a given piece, the first trim placed is selected
            winners = []
            for piece in contested_pieces:
                winner = piece.rightmost_cutter(from_trims=trim_bin)
                '''
                There might be no trims on the piece, in which case it is None
                The rightmost trim may be from a higher call of subcore
                We only place each winner in the list once
                '''
                assert winner != None
                assert winner in agents[:m]
                if winner not in winners:
                    winners.append(winner)

            ## 9: While the size of W is less than m-1
            while len(winners) < m-1:
                debug_print("BEGINNING WHILE LOOP")

                ## 10: Ignore the previous trims of agents in W, and forget previous allocations
                ''' Forget previous trims '''
                debug_print("Before forgetting in the while loop, the winners are:",winners)
                for piece in contested_pieces:
                    debug_print("before forgetting in the while loop, these are the trims on",piece)
                    for t in piece.trims:
                        debug_print(t, t.signature)
                    piece.forget_trims_by_agents(winners)
                ''' Forget allocations (pieces may have been allocated in lower calls of subcore) '''
                for piece in pieces:
                    piece.allocated = None

                ## 11: Run SubCore on the contested pieces with W as the target set of agents, 
                ## and the contested pieces only considered after the loser's trims
                subcore(contested_pieces, winners, above_ranking=current_ranking, call_signature=call_signature+' m'+str(m)+'w'+str(len(winners)))
                set_debug_prefix(call_signature)

                ## 12: Take any unallocated contested piece a. Now the rightmost trim on that piece is by a loser agent.
                ## Give that piece to that agent.
                unallocated_contested_pieces = list(filter(lambda p: p.allocated == None, contested_pieces))
                unallocated_contested_piece = unallocated_contested_pieces[0]

                debug_print("unallocated_contested_piece",unallocated_contested_piece,"has trims:")
                for t in unallocated_contested_piece.trims:
                    debug_print(t,t.signature)
                debug_print("unallocated_contested_piece final interval:",unallocated_contested_piece.intervals[-1])
                new_winner = unallocated_contested_piece.rightmost_cutter(from_trims=trim_bin)
                
                debug_print("The winners are:",winners)
                debug_print("Adding new_winner:",new_winner)
                debug_print("Agents in [:m] are",agents[:m])

                assert new_winner != None
                assert new_winner not in winners
                assert new_winner in agents[:m]
                unallocated_contested_piece.allocated = new_winner
                winners.append( new_winner )
            ## 13: END WHILE

            ## 14: Run subcore on all agents in W and the contested pieces only
            ## considered after the loser's trims. After this, |W| = m-1 and each winner has a piece
            ## allocated to them
            for piece in contested_pieces:
                debug_print("before forgetting after the while loop, these are the trims on",piece)
                for t in piece.trims:
                    debug_print(t, t.signature)
                piece.forget_trims_by_agents(winners)
                piece.allocated = None
            subcore(contested_pieces, winners, above_ranking=current_ranking, call_signature=call_signature+' m'+str(m))
            set_debug_prefix(call_signature)
            
            ''' There should be exactly one loser. '''
            losers = list(set(agents[:m]) - set(winners))
            if len(losers) != 1:
                print("Winners are:",winners)
                print("Losers  are:",losers)
                print("Agents[:m] :",agents[:m])
                assert False

            ## 15: The only loser remaining is allocated their most preferred uncontested piece
            loser = losers[0]
            preferred_uncontested_piece = loser.choose_piece(uncontested_pieces, current_ranking=current_ranking)
            preferred_uncontested_piece.allocated = loser
        ## 16: END IF/ELSE
        ## 17: Update a_i and update all benchmarks for all agents i in the set m
    ## 18: END FOR
    
    '''
    These assertions cache values that would otherwise not be cached. Be sure 
    to leave this commented for accuracy in value_count
    '''
    #assert envy_free(pieces)
    '''
    This next assertion about benchmarks should be implied by envy_free above, 
    but this is useful to remember for the proof:
    '''
    #for a in agents:
    #    assert a.benchmark <= a.get_value(a.choose_piece(pieces, count=False), count=False)
    
    debug_print("Returning from subcore with",len(pieces),"pieces and",len(agents),'agents')
    for p in pieces:
        debug_print("In this call,",p,'was allocated to',p.allocated)
    debug_print()

    ## 19: Return envy-free partial allocation for the agents
    return pieces

from agent import *
from piece import *
from debug import *


'''
Returns a neat, partial, envy-free alocation of pieces of cake among the agents given

Translation key for variables
Paper -> Code

a[i] -> agents[i].preferred_value


'''
def subcore(pieces, agents, call_signature=""):
    debug_print()
    debug_print(call_signature)
    debug_print("Calling subcore with",len(pieces),"pieces and",len(agents),'agents')

    #Ensure that no piece passed in was trimmed by an agent passed in
    for p in pieces:
        for t in p.trims:
            assert t.owner not in agents

    for m in range(1,len(agents)+1):
        debug_print("m=",m)

        # If the next agent's preferred piece is unallocated
        # IMPORTANT: This line breaks our previous upper bound for the operation of sub_core, becaus
        preferred_piece = agents[m-1].choose_piece(pieces)
        if preferred_piece.allocated == None:
            preferred_piece.allocated = agents[m-1]
        else:
            # m-1 pieces are being contested by m agents
            contested_pieces = list(filter(lambda p: p.allocated != None, pieces))
            uncontested_pieces = list(filter(lambda p: p.allocated == None, pieces))
            assert len(uncontested_pieces) >= 1

            for agent in agents[:m]:
                uncontested_max_value = max( [agent.get_value(p) for p in uncontested_pieces] )
                debug_print(agent, "uncontested max value is",float(uncontested_max_value))
                for piece in contested_pieces:
                    #Because new valuations are made from the rightmost trim, don't immediately add these new trims to the piece.
                    possible_trim =  agent.get_trim_of_value(piece, uncontested_max_value)
                    if possible_trim != None:
                        piece.pending_trims.append(possible_trim)

            #TODO should this be its own method in Piece class?
            #Now add the pending trims to the actual trims
            for piece in contested_pieces:
                piece.trims.extend(piece.pending_trims)
                #Make sure the trims are sorted by their x position
                piece.trims = sorted(piece.trims, key = lambda t: t.x)
                piece.pending_trims = []


            #Kenan asks why benchmarks are even necessary
            #They don't modify the flow of code at all, but they're used in the proof
            '''
            for agent in agents:
                agent.benchmark = max( [agent.get_value(p) for p in uncontested_pieces] )
            '''

            winners = []
            for piece in contested_pieces:
                winner = piece.rightmost_cutter()

                '''
                There might be no trims on the piece, in which case it is None
                The rightmost trim may be from a higher call of subcore
                We only place each winner in the list once
                '''
                if winner != None and \
                        winner in agents[:m] and \
                        winner not in winners:
                    winners.append(winner)

            while len(winners) < m-1:
                debug_print("BEGINNING WHILE LOOP")

                # Forget allocations
                # TODO should this go here?
                for piece in pieces:
                    piece.allocated = None

                # Forget previous trims
                for piece in contested_pieces:
                    piece.forget_trims_by_agents(winners)

                subcore(contested_pieces, winners, call_signature = call_signature+' m'+str(m)+'w')

                unallocated_contested_piece = list(filter(lambda p: p.allocated == None, contested_pieces)) [0]
                new_winner = unallocated_contested_piece.rightmost_cutter()
                
                debug_print("Adding new_winner:",new_winner)
                debug_print("Agents in [:m] are",agents[:m])
                assert new_winner != None
                assert new_winner not in winners
                assert new_winner in agents[:m]
                unallocated_contested_piece.allocated = new_winner
                winners.append( new_winner )
            #END WHILE

            # Forget previous trims
            for piece in contested_pieces:
                piece.forget_trims_by_agents(winners)
                piece.allocated = None

            subcore(contested_pieces, winners, call_signature = call_signature+' m'+str(m))
            
            losers = list(set(agents[:m]) - set(winners))
            
            ## There should be exactly one loser. If not, we have some debugging to do
            if len(losers) != 1:
                print("Winners are:",winners)
                print("Losers  are:",losers)
                print("Agents[:m] :",agents[:m])
                assert False

            loser = losers[0]
            
            preferred_uncontested_piece = loser.choose_piece(uncontested_pieces)
            preferred_uncontested_piece.allocated = loser
        # END IF/ELSE
    #END FOR
    
    #These assertions cache values that would otherwise not be cached. Be sure to leave this commented for accuracy in value_count
    '''
    assert envy_free(pieces)
    #This next assertion about benchmarks should be implied by envy_free above, but this is useful to remember for the proof:
    for a in agents:
        assert a.benchmark <= a.get_value(a.choose_piece(pieces, count=False), count=False)
    
    '''
    debug_print("Returning from subcore with",len(pieces),"pieces and",len(agents),'agents')
    debug_print()
    return pieces

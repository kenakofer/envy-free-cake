from fractions import Fraction
import random
from copy import copy
from debug import *



class Piece:

    piece_counter = 0

    def is_empty(piece):
        if piece == None:
            return True
        else:
            for i in piece.intervals:
                if i.left != i.right:
                    return False
            return True

    def extract_residue_from_pieces(pieces):
        residue = Piece([])
        for piece in pieces:
            if len(piece.trims) > 0:
                new_residue_intervals = piece.extract_residue_from_piece().intervals
                residue.intervals.extend(new_residue_intervals)
        residue.intervals.sort()
        if len(residue.intervals) > 0:
            return residue
        else:
            return None

    def extract_residue_from_piece(self):
        if len(self.trims) > 0:
            left, right = self.split_at_rightmost_trim()
            self.intervals = right.intervals
            self.trims = []
            return left
        else:
            return None

    def get_whole_piece():
        return Piece([Interval(Fraction(0), Fraction(1))])

    def __init__(self, intervals):
        self.intervals = intervals
        self.allocated = None
        self.trims = []
        self.pending_trims = []
        self.number = Piece.piece_counter
        self.name = 'Piece '+str(self.number)
        Piece.piece_counter += 1

    def __repr__(self):
        return self.name

    def __add__(self, other):
        assert self.allocated == other.allocated
        piece = copy(self)
        piece.intervals.extend(other.intervals)
        piece.intervals.sort()
        # TODO assert that intervals do not overlap?
        return piece

    def hash_info(self):
        p = self.get_after_rightmost_trim()
        return (tuple(p.intervals[:]))

    def rightmost_cutter(self, from_trims=None):
        trim = self.get_rightmost_trim(from_trims=from_trims)
        if trim != None:
            return trim.owner
        else:
            return None

    ''' 
    Get the rightmost trim on a piece. If from_trims is given, only select from trims inside from_trims.
    Break ties by the lexicography of the agents ordering, in our case, number.
    '''
    def get_rightmost_trim(self, from_trims=None):
        possible_trims = self.trims[:]
        if from_trims != None:
            possible_trims = [t for t in possible_trims if t in from_trims]
        rightmost_x = max([t.x for t in possible_trims], default=-1)
        possible_trims = [t for t in possible_trims if t.x == rightmost_x]
        possible_trims.sort(key=lambda t: t.owner.name)

        if len(possible_trims) == 0:
            return None
        return possible_trims[0]

    def get_after_rightmost_trim(self):
        trim = self.get_rightmost_trim()
        assert sorted(self.intervals) == self.intervals
        if trim != None:
            assert any( [i.left <= trim.x <= i.right for i in self.intervals] )
            for i in range(len(self.intervals)):
                if self.intervals[i].left <= trim.x < self.intervals[i].right:
                    new_interval = Interval(trim.x, self.intervals[i].right)
                    if i < len(self.intervals)-1:
                        return Piece([new_interval] + self.intervals[i+1:])
                    else:
                        return Piece([new_interval])
                elif trim.x == self.intervals[i].right:
                    if i < len(self.intervals)-1:
                        return Piece(self.intervals[i+1:])
                    else:
                        #It IS possible to trim a piece to 0 width
                        return Piece([Interval(trim.x, trim.x)])
        else:
            return copy(self)

    def split_at_rightmost_trim(self):
        trim = self.get_rightmost_trim()
        assert sorted(self.intervals) == self.intervals
        if trim == None:
            raise Exception('No trim to split at')
        assert any( [i.left <= trim.x <= i.right for i in self.intervals] )

        for i in range(len(self.intervals)):
            if self.intervals[i].left <= trim.x < self.intervals[i].right:
                new_left_interval = Interval(self.intervals[i].left, trim.x)
                new_right_interval = Interval(trim.x, self.intervals[i].right)
                if i < len(self.intervals)-1:
                    return Piece(self.intervals[:i] + [new_left_interval]), Piece([new_right_interval] + self.intervals[i+1:])
                else:
                    return Piece(self.intervals[:i] + [new_left_interval]), Piece([new_right_interval])
            elif trim.x == self.intervals[i].right:
                if i < len(self.intervals)-1:
                    return Piece(self.intervals[:i+1]), Piece(self.intervals[i+1:])
                else:
                    #It IS possible to trim a piece to 0 width
                    return Piece(self.intervals[:]), Piece([Interval(trim.x, trim.x)])

    '''
    If prefix_signature is given, will only forget trims whose signatures that begin with the prefix_signature
    '''
    def forget_trims_by_agents(self, agents, prefix_signature=None, with_m=None):
        if prefix_signature == None:
            self.trims = list(filter(lambda t: t.owner not in agents, self.trims))
        else:
            self.trims = [t for t in self.trims if t.owner not in agents or (not prefix_signature in t.signature) or (prefix_signature == t.signature and with_m != t.m)]

class Interval:

    def __init__(self, left, right):
        self.left = left
        self.right = right
        assert left <= right
        assert type(self.left) == Fraction
        assert type(self.right) == Fraction

    def overlaps(self, other):
        return self.left < other.right and self.right > other.left

    def __repr__(self):
        return '['+str(float(self.left))[:5]+', '+str(float(self.right))[:5]+']'

    def __hash__(self):
        return hash((self.left, self.right))

    def __eq__(self,other):
        return self.right == other.right and self.left == other.left

    def __lt__(self, other):
        return self.left < other.left

class Trim:

    def __init__(self, owner, location):
        self.x = location
        assert type(self.x) == Fraction
        self.owner = owner
        self.signature = ''

    def __repr__(self):
        return 'Trim('+str(self.owner)+', '+str(float(self.x))+')'

def envy_free(pieces):
    debug_print("Envy free check!")
    for p in pieces:
        if p.allocated != None:
            agent = p.allocated
            debug_print(agent,"is allocated this piece:",p,"which has value",float(agent.get_value(p, count=False)))
            debug_print("They would prefer a piece of value:",float(agent.get_value(agent.choose_piece(pieces, count=False))))
            if agent.get_value(agent.choose_piece(pieces)) > agent.get_value(p):
                return False
    return True

import random
from copy import copy
from fractions import Fraction
from debug import *


class Agent:

    def myrandom(x):
        return random.random()
    '''
    Creates preference functions for valuing and trimming cake, which can appoximate any function of one argument 0 <= x <= 1.
    division_count gives the number of homogeneous segments to divide the cake into. A larger number better approximates the
    function. The default function to use is a wrapper of random.random() that takes x
    '''
    def generate_preference_functions_from_function(self, division_count, preference_function):
        division_values = {}
        #Generated evenly spaced values outputted from the function (random by default)
        for i in range(1,division_count+1):
            x = Fraction(i,division_count)
            division_values[x] = Fraction(preference_function(x))
        s = sum([ division_values[k] for k in division_values])
        factor = division_count / s
        #Adjusted Division Values
        adv = {k: division_values[k]*factor for k in division_values}
        return self.generate_preference_functions_from_adv(adv)
    
    def generate_preference_functions_from_adv(self, adv):
        #Check that the adjusted division values indeed add to the number of divisions
        count = 0
        for k in adv:
            count += adv[k]
        assert count == len(adv)
        self.adv = adv
        keys = list(adv.keys())
        keys.sort()

        def value_up_to(x):
            assert type(x) == Fraction
            acc_value = Fraction(0)
            for i in range(len(keys)):
                if x >= keys[i]:
                    if i==0:
                        acc_value += adv[keys[i]] * keys[i]
                    else:
                        acc_value += adv[keys[i]] * (keys[i]-keys[i-1])
                else:
                    if i==0:
                        acc_value += adv[keys[i]] * x
                    else:
                        acc_value += adv[keys[i]] * (x-keys[i-1])
                    break
            assert type(acc_value) == Fraction
            return acc_value

        '''
        Given a slice and a value, the agent must be able to determine where to trim the slice so that it is worth the value. Returns the trim and does not add it to the piece
        '''
        def get_trim_of_value(piece, desired_value, count=True):
            assert type(desired_value) == Fraction

            if count: self.trim_count += 1

            if len(piece.trims) > 0:
                return get_trim_of_value(piece.get_after_rightmost_trim(), desired_value, count=False)

            acc_value = Fraction(0)
            trim_at = Fraction(0)
            #target_value is the amount to trim OFF of the piece after the rightmost trim
            target_value = self.get_value(piece, count=False) - desired_value
            if target_value < 0:
                return None
            for interval in piece.intervals:
                value_of_interval = value_up_to(interval.right) - value_up_to(interval.left)

                if acc_value + value_of_interval < target_value:
                    acc_value += value_of_interval
                elif acc_value + value_of_interval > target_value:
                    #Start using preference divisions
                    if trim_at == 0:
                        trim_at = interval.left

                    for k in filter( lambda k: trim_at < k, keys ):
                        if value_up_to(k) - value_up_to(trim_at) + acc_value <= target_value:
                            acc_value += value_up_to(k) - value_up_to(trim_at)
                            trim_at = k
                        else:
                            trim_at += (target_value - acc_value) / adv[k]
                            break
                    break

                #elif acc_value == target_value:
                else:
                    trim_at = interval.right
                    break

            #Because this trim may not be added to the piece, hash the value of a copied piece
            new_piece = copy(piece)
            new_piece.trims = [Trim(self, trim_at)]
            self.cached_values[new_piece.hash_info()] = desired_value

            return Trim(self, trim_at)

        return value_up_to, get_trim_of_value

    '''
    When created, all an agent has is a function for valuing different slices of cake
    '''
    def __init__(self, division_count = 10, preference_function=myrandom):
        self.value_up_to, self.get_trim_of_value = self.generate_preference_functions_from_function(division_count, preference_function)
        self.name = 'Agent '+str(random.randint(10000,99999))
        self.trim_count = 0
        self.value_count = 0
        #This dictionary stores the cached values of pieces, with hash of piece as keys, and value of piece as value
        self.cached_values = {}

    def __repr__(self):
        return self.name

    '''
    Given a list of slices, the agent must be able to identify their favorite. There must be no ties
    Also, if there is a tie between an allocated piece and an unallocated piece, choose an unallocated one
    TODO don't reevaluate all these get_value calls
    '''
    def choose_piece(self, pieces, count=True):
        max_value = 0
        best_piece = None
        for p in pieces:
            max_value = max(max_value, self.get_value(p, count=count))
        for p in pieces:
            if self.get_value(p, count=False) == max_value:
                if p.allocated == None:
                    #Immediately return an unallocated piece that we come across
                    return p
                elif best_piece==None:
                    best_piece = p

        assert best_piece != None
        #We didn't find any unallocated pieces
        return best_piece

    '''
    Given a slice, the agent must be able to assign consistent, proportional value to the slice 
    '''
    def get_value(self, piece, count=True, whole_piece=False, use_cache=True):
        if use_cache and piece.hash_info() in self.cached_values and not whole_piece:
            return self.cached_values[piece.hash_info()]

        if count: 
            self.value_count +=1
        if whole_piece:
            cut_piece = piece
        else:
            cut_piece = piece.get_after_rightmost_trim()

        sum_value = 0
        for interval in cut_piece.intervals:
            sum_value += self.value_up_to(interval.right) - self.value_up_to(interval.left)

        #Cache the computed value
        self.cached_values[piece.hash_info()] = sum_value
        return sum_value

    '''
    Recursively cut pieces off the right side
    '''
    def cut_into_n_pieces_of_equal_value(self, n, piece):
        if n <= 1:
            return [piece]
        total_value = self.get_value(piece)
        target_value = total_value / n
        assert type(target_value) == Fraction 
        left_piece = copy(piece)
        pieces = []
        for i in range(n-1):
            t = self.get_trim_of_value(left_piece, target_value)
            assert t.x != 0
            left_piece.trims.append(t)
            assert left_piece.get_rightmost_trim() == t
            left_piece, right_piece = left_piece.split_at_rightmost_trim()

            pieces.append(right_piece)
        #Pieces were added in the wrong order, so reverse!
        pieces.append(left_piece)
        pieces.reverse()
        #Cache all the piece values
        #for p in pieces:
        #    self.cached_values[p.hash_info()] = target_value
        return pieces


    '''
    Output the agent's preference function into a string that can be imported as well
    '''
    def get_preference_string(self):
        string = ""
        for k in sorted(self.adv.keys()):
            f = self.adv[k]
            string += str(f.numerator) + ' ' + str(f.denominator) + ', '
        return string[:-2] #Remove last comma and space

    '''
    Import a preference string of the form of that which was outputted
    '''
    def set_preferences(self, preference_string):
        fraction_string_list = preference_string.split(',')
        self.adv = {}
        interval = Fraction(1, len(fraction_string_list))
        x = Fraction(0)
        for f_s in fraction_string_list:
            x += interval
            num = int(f_s.split()[0])
            den = int(f_s.split()[1])
            self.adv[x] = Fraction(num, den)
        assert x == Fraction(1,1)
        assert sum([self.adv[k] for k in self.adv]) == len(fraction_string_list)
        self.value_up_to, self.get_trim_of_value = self.generate_preference_functions_from_adv(self.adv)



class Cake:
    
    def __init__(self):
        self.pieces = [Piece(self, [Interval(Fraction(0), Fraction(1))])] #Begin with a single slice the size of the cake

class Piece:

    def __init__(self, cake, intervals):
        self.cake = cake
        self.intervals = intervals
        self.allocated = None
        self.trims = []
        self.pending_trims = []
        self.tags = [] #Use tags to mark pieces with additional information. For example, if someone claims a piece.
        self.name = 'Piece '+str(random.randint(10000,99999))

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.hash_info())

    def hash_info(self):
        t = self.get_rightmost_trim()
        if t != None:
            right = t.x
        else:
            right = self.intervals[0].left
        return (tuple(self.intervals[:]), right)

    def rightmost_cutter(self):
        trim = self.get_rightmost_trim()
        if trim != None:
            return trim.owner
        else:
            return None

        #TODO sort trims first by position, then by lexicography

    def get_rightmost_trim(self):
        trim = None
        for t in self.trims:
            if trim == None or t.x > trim.x:
                trim = t
        return trim

    def get_after_rightmost_trim(self):
        trim = self.get_rightmost_trim()
        if trim != None:
            assert any( [i.left <= trim.x <= i.right for i in self.intervals] )
            for i in range(len(self.intervals)):
                if self.intervals[i].left <= trim.x < self.intervals[i].right:
                    new_interval = Interval(trim.x, self.intervals[i].right)
                    if i < len(self.intervals)-1:
                        return Piece(self.cake, [new_interval] + self.intervals[i+1:])
                    else:
                        return Piece(self.cake, [new_interval])
                elif trim.x == self.intervals[i].right:
                    if i < len(self.intervals)-1:
                        return Piece(self.cake, self.intervals[i+1:])
                    else:
                        #It IS possible to trim a piece to 0 width
                        return Piece(self.cake, [Interval(trim.x, trim.x)])
        else:
            return copy(self)

    def split_at_rightmost_trim(self):
        trim = self.get_rightmost_trim()
        if trim == None:
            raise Exception('No trim to split at')
        assert any( [i.left <= trim.x <= i.right for i in self.intervals] )

        for i in range(len(self.intervals)):
            if self.intervals[i].left <= trim.x < self.intervals[i].right:
                new_left_interval = Interval(self.intervals[i].left, trim.x)
                new_right_interval = Interval(trim.x, self.intervals[i].right)
                if i < len(self.intervals)-1:
                    return Piece(self.cake, self.intervals[:i] + [new_left_interval]), Piece(self.cake, [new_right_interval] + self.intervals[i+1:])
                else:
                    return Piece(self.cake, self.intervals[:i] + [new_left_interval]), Piece(self.cake, [new_right_interval])
            elif trim.x == self.intervals[i].right:
                if i < len(self.intervals)-1:
                    return Piece(self.cake, self.intervals[:i+1]), Piece(self.cake, self.intervals[i+1:])
                else:
                    #It IS possible to trim a piece to 0 width
                    return Piece(self.cake, self.intervals[:]), Piece(self.cake, [Interval(trim.x, trim.x)])

    def forget_trims_by_agents(self, agents):
        keep_trims = list(filter(lambda t: t.owner not in agents, self.trims))
        self.trims = keep_trims


class Interval:

    def __init__(self, left, right):
        self.left = left
        self.right = right
        assert type(self.left) == Fraction
        assert type(self.right) == Fraction

    def __repr__(self):
        return '['+str(float(self.left))[:5]+', '+str(float(self.right))[:5]+']'

    def __hash__(self):
        return hash((self.left, self.right))

    def __eq__(self,other):
        return self.right == other.right and self.left == other.left

class Trim:

    def __init__(self, owner, location):
        self.x = location
        assert type(self.x) == Fraction
        self.owner = owner

    def __repr__(self):
        return 'Trim('+str(self.owner)+', '+str(float(self.x))+')'

def envy_free(pieces):
    debug_print("Envy free check!")
    for p in pieces:
        if p.allocated != None:
            agent = p.allocated
            debug_print(agent,"is allocated this piece:",p,"which has value",float(agent.get_value(p, count=False)))
            debug_print("Said agent would prefer a piece of value:",float(agent.get_value(agent.choose_piece(pieces, count=False), count=False)))
            if agent.get_value(agent.choose_piece(pieces, count=False), count=False) > agent.get_value(p, count=False):
                return False
    return True

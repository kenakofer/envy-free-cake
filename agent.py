import piece as piece_mod #To avoid name clashes
from fractions import Fraction
import random
from copy import copy
from itertools import combinations
from debug import *

class Agent:

    def get_dominations(agents, pieces, residue):
        for p in pieces:
            if p.allocated != None:
                #Make it easier to reference an agent's allocated piece
                p.allocated.piece = p
        for a1 in agents:
            a1.dominations = set([])
            for a2 in agents:
                #Test if a1 dominates a2
                dominates = a1.get_value(a1.piece) >= a1.get_value(a2.piece) + a1.get_value(residue)
                if dominates:
                    a1.dominations.add(a2)

    # TODO this is order 2^n. Is there a better way?
    def get_dominating_set(agents, pieces, residue):
        Agent.get_dominations(agents, pieces, residue)
        for n in range(len(agents)-1, 0, -1):
            possibilities = set(combinations(agents, n))
            for possibility in possibilities:
                dominators = set(possibility)
                dominated = set(agents) - dominators
                good = True
                for d1 in dominators:
                    for d2 in dominated:
                        if not d2 in d1.dominations:
                            good = False
                            break
                    if not good:
                        break
                if good:
                    return (dominators, dominated)

        return None

    def myrandom(x):
        return random.random()


    '''
    Creates preference functions for valuing and trimming cake, which can appoximate any function of one argument 0 <= x <= 1.
    division_count gives the number of homogeneous segments to divide the cake into. A larger number better approximates the
    function. The default function to use is a wrapper of random.random() that takes x
    '''
    def set_adv_from_function(self, division_count, preference_function):
        division_values = {}
        #Generated evenly spaced values outputted from the function (random by default)
        for i in range(1,division_count+1):
            x = Fraction(i,division_count)
            division_values[x] = Fraction(preference_function(x))
        s = sum([ division_values[k] for k in division_values])
        factor = division_count / s
        #Adjusted Division Values
        self.adv = {k: division_values[k]*factor for k in division_values}

    def value_up_to(self, x):
        assert type(x) == Fraction
        acc_value = Fraction(0)
        keys = list(self.adv.keys())
        keys.sort()
        for i in range(len(keys)):
            if x >= keys[i]:
                if i==0:
                    acc_value += self.adv[keys[i]] * keys[i]
                else:
                    acc_value += self.adv[keys[i]] * (keys[i]-keys[i-1])
            else:
                if i==0:
                    acc_value += self.adv[keys[i]] * x
                else:
                    acc_value += self.adv[keys[i]] * (x-keys[i-1])
                break
        assert type(acc_value) == Fraction
        return acc_value

    '''
    Given a slice and a value, the agent must be able to determine where to trim the slice so that it is worth the value. Returns the trim and does not add it to the piece
    '''
    def get_trim_of_value(self, piece, desired_value, count=True):
        assert type(desired_value) == Fraction
        assert sorted(piece.intervals) == piece.intervals

        keys = list(self.adv.keys())
        keys.sort()

        # TODO should we always increment trim_count?
        if count: self.trim_count += 1

        if len(piece.trims) > 0:
            return self.get_trim_of_value(piece.get_after_rightmost_trim(), desired_value, count=False)

        acc_value = Fraction(0)
        trim_at = Fraction(0)
        #target_value is the amount to trim OFF of the piece after the rightmost trim
        # We agreed that if we incremented trim_count, the get_value should not count
        target_value = self.get_value(piece, count=False) - desired_value
        if target_value < 0:
            return None
        for interval in piece.intervals:
            value_of_interval = self.value_up_to(interval.right) - self.value_up_to(interval.left)

            if acc_value + value_of_interval < target_value:
                acc_value += value_of_interval
            elif acc_value + value_of_interval > target_value:
                #Start using preference divisions
                if trim_at == 0:
                    trim_at = interval.left

                for k in filter( lambda k: trim_at < k, keys ):
                    if self.value_up_to(k) - self.value_up_to(trim_at) + acc_value <= target_value:
                        acc_value += self.value_up_to(k) - self.value_up_to(trim_at)
                        trim_at = k
                    else:
                        trim_at += (target_value - acc_value) / self.adv[k]
                        break
                break

            #elif acc_value == target_value:
            else:
                trim_at = interval.right
                break

        #Because this trim may not be added to the piece, hash the value of a copied piece
        new_piece = copy(piece)
        new_piece.trims = [piece_mod.Trim(self, trim_at)]
        self.cached_values[new_piece.hash_info()] = desired_value

        return piece_mod.Trim(self, trim_at)

    '''
    When created, all an agent has is a function for valuing different slices of cake
    '''
    def __init__(self, division_count = 10, preference_function=myrandom):
        self.set_adv_from_function(division_count, preference_function)
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

            if self.get_value(p) == max_value:
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
        if count:
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
        #Cache the left piece's value
        self.cached_values[left_piece.hash_info()] = target_value
        pieces.reverse()
        #Assert that all pieces have indeed been hashed (which mostly happens inside the trim function)
        for p in pieces:
            assert p.hash_info() in self.cached_values

        return pieces

    def fractalize_preferences(self, residue_intervals, subdivisions=10, preference_function=myrandom):
        fixed_points = list(self.adv.keys())
        for key in self.cached_values:
            for interval in key:
                fixed_points.append( interval.left )
                fixed_points.append( interval.right )
        fixed_points = sorted(list(set(fixed_points)))
        intervals = [piece_mod.Interval(fixed_points[i], fixed_points[i+1]) for i in range(0, len(fixed_points)-1)]
        intervals = list(filter(lambda i: any([i.overlaps(r_i) for r_i in residue_intervals]), intervals))

        new_keys = {}
        i = 0
        for x in self.adv.keys():
            pref_height = self.adv[x]

            while intervals[i].left < x:
                pref_width = intervals[i].right - intervals[i].left
                pref_area = pref_height * pref_width
                new_pref_width = pref_width / Fraction(subdivisions)
                accumulated_area = 0
                for i2 in range( 1, subdivisions+1):

                    x2 = intervals[i].left + i2 * new_pref_width
                    new_pref_height = Fraction(preference_function(x2))
                    new_pref_area = new_pref_height * new_pref_width
                    accumulated_area += new_pref_area
                    new_keys[x2] =  new_pref_height # TODO talk with David because weird function stuff ???
                #Now scale the intervals
                
                factor = pref_area / accumulated_area
                accumulated_area = 0
                for i2 in range( 1, subdivisions+1):
                    x2 = intervals[i].left + i2 * new_pref_width
                    new_keys[x2] *= factor
                    accumulated_area += new_keys[x2] * new_pref_width
                # Certify that the area under the curve is the same as before
                assert accumulated_area == pref_area

                i += 1
                if i >= len(intervals):
                    break

            if i >= len(intervals):
                break

        self.adv.update(new_keys)

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

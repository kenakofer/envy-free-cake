import random
from copy import copy
from fractions import Fraction

class Agent:

    #TODO some hardcore testing!!!!!
    #Also maybe some hardcore documentation.

    def generate_random_preferences(self, division_count):
        division_values = { Fraction(i,division_count): Fraction(random.random()) for i in range(1,division_count+1)}
        s = sum([ division_values[k] for k in division_values])
        factor = division_count / s
        #Adjusted Division Values
        adv = {k: division_values[k]*factor for k in division_values}
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
        def get_trim_of_value(piece, desired_value, actually_divide=False):
            assert type(desired_value) == Fraction

            if len(piece.trims) > 0:
                return get_trim_of_value(piece.get_after_rightmost_trim(), desired_value, actually_divide = actually_divide)

            acc_value = Fraction(0)
            trim_at = Fraction(0)
            #target_value is the amount to trim OFF of the piece after the rightmost trim
            target_value = self.get_value(piece) - desired_value
            if target_value <= 0:
                return None
            for interval in piece.intervals:
                value_of_interval = value_up_to(interval.right) - value_up_to(interval.left)
                #print("This interval is worth",value_of_interval)

                if acc_value + value_of_interval < target_value:
                    #print("Which will not be enough to reach target value of",target_value)
                    acc_value += value_of_interval
                    #print("Now acc_value is",acc_value)
                elif acc_value + value_of_interval > target_value:
                    #Start using preference divisions
                    #print('Which will take us above the target value of',target_value)
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
                    #print("Placing trim at",trim_at)
                    break
            if not actually_divide:
                return Trim(self, trim_at)
            else:
                #TODO FINISH!!!
                assert False
                p_left  = Piece(piece.cake, [])
                p_right = Piece(piece.cake, [])

        return value_up_to, get_trim_of_value

    '''
    When created, all an agent has is a function for valuing different slices of cake
    '''
    def __init__(self, div_count = 10):
        self.value_up_to, self.get_trim_of_value = self.generate_random_preferences(div_count)
        self.name = 'Agent '+str(random.randint(10000,99999))

    def __repr__(self):
        return self.name

    '''
    Given a list of slices, the agent must be able to identify their favorite. There must be no ties
    '''
    def choose_piece(self, pieces):
        max_value = 0
        for p in pieces:
            max_value = max(max_value, self.get_value(p))
        for p in pieces:
            if self.get_value(p) == max_value:
                return p
        raise Error('Could not find a best piece')

    '''
    Given a slice, the agent must be able to assign consistent, proportional value to the slice 
    '''
    def get_value(self, piece):
        sum_value = 0
        cut_piece = piece.get_after_rightmost_trim()
        for interval in cut_piece.intervals:
            sum_value += self.value_up_to(interval.right) - self.value_up_to(interval.left)
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
        t = self.get_trim_of_value(piece, target_value)
        piece.trims.append(t)
        left_piece, right_piece = piece.split_at_rightmost_trim()
        return self.cut_into_n_pieces_of_equal_value(n-1, left_piece) + [right_piece]


    '''
    Must be able to output their preference function into a string that can be imported as well
    '''
    def get_preferences(self):
        assert False

    '''
    Must be able to import a preference string
    '''
    def set_preferences(self, preferences):
        assert False

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
                    return Piece(self.cake, self.intervals), Piece(self.cake, [Interval(trim.x, trim.x)])

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
        return '['+str(self.left)+', '+str(self.right)+']'

class Trim:

    def __init__(self, owner, location):
        self.x = location
        assert type(self.x) == Fraction
        self.owner = owner

def envy_free(pieces):
    print("Envy free check!")
    for p in pieces:
        if p.allocated != None:
            agent = p.allocated
            print(agent,"is allocated this piece:",p,"which has value",float(agent.get_value(p)))
            print("Said agent would prefer a piece of value:",float(agent.get_value(agent.choose_piece(pieces))))
            if agent.get_value(agent.choose_piece(pieces)) > agent.get_value(p):
                return False
    return True

from classes import *
from core import *

OUTFILE = './data.out'

def core_random(agent_number):
    divisions = 10
    agents = [Agent(division_count=divisions) for i in range(agent_number)]
    write_scenario_to_file(agents, OUTFILE)

    

def write_scenario_to_file(agents, filename):
    info_line = ""
    for a in agents:
        info_line += a.get_preference_string() + '; '
    try:
        core(agents[0], agents, Piece.get_whole_piece())
    except AssertionError:
        print("We hit a False Assertion! Here is the agent data to reproduce:")
        print(info_line)
        raise
    value_count= sum([a.value_count for a in agents])
    trim_count = sum([a.trim_count for a in agents])
    
    info_line += '| '
    info_line += str(trim_count) + ' | '
    info_line += str(value_count)
    with open(filename, 'a') as f:
        print(info_line, file=f)


def core_worst_case():
        debug_print("Testing a possible worst case call to prints")
        for n in range(4,12):
            print(n)
            divs = 30
            agents = [
                Agent(division_count=divs, preference_function=lambda x: x**i) for i in range(1, n+1)
            ]
            write_scenario_to_file(agents, OUTFILE)
            #print("sum:",trim_count+value_count)
            #self.assertTrue( value_count + trim_count <= worst_cases_for_n_players[n] )


if __name__ == '__main__':
    for n in range(8,12):
        for i in range(1000):
            core_random(n)

from agent import *
from piece import *
from core import *
from random import randint
from envy_free_allocation import *

OUTFILE = './data_envy_free.out'

def write_output(string):
    with open(OUTFILE, 'a') as f:
        print(string, file=f)

def write_core_scenario_to_file(agents):
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
    write_output(info_line)

def write_envy_free_scenario_to_file(agents):
    info_line = ""
    try:
        core_number = get_envy_free_allocation(agents, Piece.get_whole_piece(), get_call_number=True)
    except AssertionError:
        print("We hit a False Assertion! Here is the agent data to reproduce:")
        print(info_line)
        raise
    for a in agents:
        info_line += a.get_preference_string() + '; '
    
    info_line += '| '
    info_line += str(core_number)
    write_output(info_line)

def envy_free_random(player_number_list, count):
    for n in player_number_list:
        print(n,'Players')
        write_output('# Random cases for '+str(n)+' Agents')
        for i in range(count):
            print(str(i)+'th trial for '+str(n)+' players')
            agents = [Agent(division_count=randint(10,20)) for i in range(n)]
            write_envy_free_scenario_to_file(agents)

def core_random(player_number_list, count):
    for n in player_number_list:
        for i in range(count):
            agents = [Agent(division_count=randint(10,20)) for i in range(n)]
            write_core_scenario_to_file(agents)

def core_worst_case(player_number_list):
        debug_print("Testing a possible worst case call")
        for n in player_number_list:
            write_output('# Worst (???) case for '+str(n)+' Agents')
            print(n)
            divs = 30
            agents = [
                Agent(division_count=divs, preference_function=lambda x: x**i) for i in range(1, n+1)
            ]
            write_core_scenario_to_file(agents)
            #print("sum:",trim_count+value_count)

def core_best_case(player_number_list):
        debug_print("Testing a possible best case call")
        for n in player_number_list:
            print(n)
            write_output('# Best case for '+str(n)+' Agents')
            divs = 1
            agents = [
                Agent(division_count=divs, preference_function=lambda x: 1) for i in range(1, n+1)
            ]
            write_core_scenario_to_file(agents)
            #print("sum:",trim_count+value_count)


if __name__ == '__main__':
    envy_free_random(range(4,11),100)
    #core_best_case(range(4,12))
    #core_worst_case(range(4,12))
    #core_random(range(4,12),1000)

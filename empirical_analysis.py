from agent import *
from piece import *
from core import *
from random import randint
from envy_free_allocation import *
from copy import copy

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

def genetic_find_worst_envy_free_case(agent_number, population_size=9, cull_number=6):
    #Create population. Each member of the population is a group of agents
    population = [[Agent(division_count=50) for i in range(agent_number)] for n in range(population_size)]
    #Evaluate fitness based on number of core runs required
    while True:
        fitness = {}
        for p in population:
            core_number = get_envy_free_allocation(p, Piece.get_whole_piece(), get_call_number=True, fractalize=False)
            print(' ',core_number,hash(tuple(p)))
            fitness[tuple(p)] = core_number
        #Remove lowest 2/3 of the population
        fit_list = [(k,fitness[k]) for k in fitness]
        random.shuffle(fit_list)
        fit_list.sort(key=lambda x: x[1])
        print('Best fitness:', fitness[fit_list[-1][0]])
        fit_list = fit_list[cull_number:]
        #Reproduce to make the next generation
        #Turn fit_list into a simple list of lists of agents
        fit_list = [p[0] for p in fit_list]
        next_gen = fit_list[:]
        for p in fit_list + fit_list:
            next_gen.append(variate_agent_preferences(p))
        population = next_gen


def variate_agent_preferences(agents, mutation_frequency=.1, variation_amount=.2):
    new_agents = []
    advs = [copy(a.adv) for a in agents]
    for adv in advs:
        for k in adv:
            if random.random() < mutation_frequency:
                adv[k] = max(0, adv[k] + Fraction((random.random()*2 - 1) * variation_amount))
        s = sum([ adv[k] for k in adv])
        factor = Fraction(len(adv), s)
        #Adjusted Division Values
        adv = {k: adv[k]*factor for k in adv}
        new_agent = Agent()
        new_agent.adv = adv
        new_agents.append(new_agent)
    return new_agents

if __name__ == '__main__':
    genetic_find_worst_envy_free_case(4)
    #envy_free_random(range(4,11),100)
    #core_best_case(range(4,12))
    #core_worst_case(range(4,12))
    #core_random(range(4,12),1000)

#!/usr/bin/env python3
from agent import *
from piece import *
from core import *
import random
from envy_free_allocation import *
from copy import copy
from time import time

seed = 0

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

def write_envy_free_scenario_to_file(agents, division_function=get_envy_free_allocation):
    info_line = ""
    try:
        core_number, trim_count, value_count = division_function(agents, Piece.get_whole_piece(), get_counts=True)
    except AssertionError:
        print("We hit a False Assertion! Here is the seed to reproduce:", seed)
        print(info_line)
        return
        #raise
    for a in agents:
        info_line += a.get_preference_string() + '; '
    
    info_line += ' | '
    info_line += str(core_number)
    info_line += ' | '
    info_line += str(trim_count)
    info_line += ' | '
    info_line += str(value_count)
    write_output(info_line)

def envy_free_random(player_number_list, count, division_function=get_envy_free_allocation):
    global seed
    for n in player_number_list:
        print(n,'Players')
        write_output('# Random cases for '+str(n)+' Agents')
        for i in range(count):
            seed = int(time()*1000)
            random.seed(seed)
            print(str(i)+'th trial for '+str(n)+' players')
            agents = [Agent(division_count=20) for i in range(n)]
            write_envy_free_scenario_to_file(agents, division_function=division_function)

def core_random(player_number_list, count):
    for n in player_number_list:
        for i in range(count):
            agents = [Agent(division_count=random.randint(10,20)) for i in range(n)]
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

def genetic_find_worst_envy_free_case(population, cull_number=-1, epsilon_change=-1):
    #Create population. Each member of the population is a group of agents
    if cull_number < 0:
        cull_number = len(population) * 2 // 3
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
            next_gen.append(variate_agent_preferences(p, epsilon_change=epsilon_change))
        population = next_gen


def variate_agent_preferences(agents, mutation_frequency=.1, variation_amount=.5, epsilon_change=-1):
    new_agents = []
    advs = [copy(a.adv) for a in agents]
    for adv in advs:
        for k in adv:
            if random.random() < mutation_frequency:
                if epsilon_change > 0:
                    adv[k] += random.randint(-1,1) * epsilon_change
                else:
                    adv[k] = max(0, adv[k] + Fraction((random.random()*2 - 1) * variation_amount))
        keys = sorted(list(adv.keys()))
        acc_area = Fraction(0)
        for i in range(len(keys)):
            left = keys[i-1] if i>0 else 0
            right = keys[i]
            width = Fraction(right-left)
            acc_area += adv[keys[i]] * width
        factor = Fraction(len(adv), acc_area)
        #Adjusted Division Values
        adv = {k: adv[k]*factor for k in adv}
        new_agent = Agent()
        new_agent.adv = adv
        new_agents.append(new_agent)
    return new_agents

def get_agents_partitioned_preferences(number, division_count=48):
    agents = [Agent(division_count=division_count) for i in range(number)]
    indices_remaining = set(range(division_count))
    for a in agents:
        indices = set(random.sample(indices_remaining, division_count // number))
        indices_remaining -= indices
        for i in range(len(a.adv)):
            a.adv[i] = Fraction(random.random()) if i in indices else 0
    return agents

if __name__ == '__main__':
    #population = [get_agents_partitioned_preferences(4, division_count=400) for i in range(9)]
    #population = [[Agent(division_count=50, preference_function=lambda x: x) for i in range(4)] for n in range(9)]
    #genetic_find_worst_envy_free_case(population, epsilon_change=Fraction(1, 2**16))
    #population = [[Agent(division_count=50) for i in range(4)] for n in range(9)]
    #genetic_find_worst_envy_free_case(population)
    #envy_free_random(range(13,14),100)
    #envy_free_random(range(3,8), 100, division_function=get_waste_makes_haste_envy_free_allocation)
    for n in range(7,11):
        for i in range(20):
            OUTFILE = './data_envy_free_core.out'
            envy_free_random(range(n,n+1), 1, division_function=get_envy_free_allocation)
            OUTFILE = './data_envy_free_waste_makes_haste.out'
            envy_free_random(range(n,n+1), 1, division_function=get_envy_free_allocation)


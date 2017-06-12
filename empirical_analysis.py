from classes import *
from core import *

OUTFILE = './data.out'

def core_random(agent_number):
    divisions = 10
    agents = [Agent(division_count=divisions) for i in range(agent_number)]
    cake = Cake()
    core(agents[0], agents, cake.pieces[0])
    value_count= sum([a.value_count for a in agents])
    trim_count = sum([a.trim_count for a in agents])
    info_line = ""
    for a in agents:
        info_line += a.get_preference_string() + '; '
    info_line += '| '
    info_line += str(trim_count) + ' | '
    info_line += str(value_count)
    with open(OUTFILE, 'a') as f:
        print(info_line, file=f)




if __name__ == '__main__':
    for i in range(1000):
        core_random(5)

# envy-free-cake
An implementation of the protocol proposed by [Aziz and Mackenzie](https://arxiv.org/pdf/1604.03655.pdf) (2016) for discrete, bounded, envy-free, complete division of a heterogeneous resource, often referred to as cake.

Until 2016, it was an open question in computer science whether such an algorithm existed. Aziz and Mackenzie's algorithm is bounded on the order of <code>n^n^n^n^n^n</code>, where n is the number of agents dividing the resource.

Though empirically running the entirety of their protocol is infeasible for modern computing, some modules of the code are quite manageable even with the worst case. Modules which we have tested in their entirety for correctness include:

 - Core and Subcore (tested up to 15 agents): Core takes a set of agents with preferences and a piece of cake and returns trimmed pieces of that cake such that no agent values another agent's allocated piece over their own. Core calls subcore, and subcore recursively calls itself.
 
The python notebook file contains experimental methods for visualizing the status of pieces of cake, agents, and preferences. 

The python files beginning with <code>test_</code> are unit tests for the correctness of the modules. 

This repository is being regularly updated by a research team at Goshen College in the summer of 2017.

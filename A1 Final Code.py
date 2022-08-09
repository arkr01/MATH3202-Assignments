# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 11:41:02 2021
"""
from gurobipy import *

# Electrigrid Final Solution

# Sets/Data

# Importing nodes from given dataset
nodesfile = open('nodes2.csv', 'r')
nodeslist = [list(map(int, w.strip().split(','))) for w in nodesfile if 'Node' not in w]
nodes = [{'number': w[0], 'x': w[1], 'y': w[2], 'demand': [w[3], w[4], w[5], w[6], w[7], w[8]]} for
         w in nodeslist]

# Importing arcs from given dataset
gridfile = open('grid.csv', 'r')
gridlist = [list(map(int, w.strip().split(','))) for w in gridfile if 'Arc' not in w]

# 0.1% power loss per km in each transmission line
powerLoss = 0.001

# Add efficiency of each arc using Euclidean Distance formula
arcs = [{'Arc Number': w[0], 'Node1': w[1], 'Node2': w[2], 'Efficiency': 1 - (math.sqrt(pow(
        nodes[w[1]]['x'] - nodes[w[2]]['x'], 2) + pow(nodes[w[1]]['y'] - nodes[w[2]]['y'], 2)) *
        powerLoss)} for w in gridlist]

# Stores the generators nodes. Note: the generators are found in a file using a for loop, checking
# for nodes with demand = 0
generator = []

# Stores the generator node numbers in ascending order
generatorNo = []

# Time periods in a day (i.e. 0 corresponds to 12am - 4am, 1 corresponds to 4am - 8am, etc.)
time = [0, 1, 2, 3, 4, 5]

# Duration of a time period (i.e. 4 hours)
timePeriodDuration = 4

# Cost of each generator (in the same order as generatorNo)
costs = [77, 75, 62, 78]

# Capacity of each generator (in the same order as generatorNo)
capacity = [580, 754, 377, 745]

# Current index of generator
index = 0

# Find the generators in the list of nodes and add them to the generator set
for n in nodes:
    if n['demand'][0] == 0:
        temp = {"Number": n['number'], "Cost": costs[index], "Capacity": capacity[index]}
        generator.append(temp)
        generatorNo.append(n['number'])
        index += 1

# Unrestricted transmission lines, effectively handling any load
Unrestricted = [66, 67, 68, 69, 92, 93, 104, 105, 108, 109, 138, 139, 142, 143, 144, 145, 158, 159]

# Power limit for all restricted arcs
powerLimit = 83

# Maximum change in generator power allowed between each time period
powerChange = 148

G = range(len(generator))
N = range(len(nodes))
A = range(len(arcs))
m = Model("Electrigrid")

# Variables

# The amount of electricity to produce from each generator (MW/hr), at the beginning of any given
# time period
X = {(g, t): m.addVar() for g in G for t in time}

# The amount of power in each arc at the beginning of the time period (MW/hr), not considering
# efficiency
Y = {(a, t): m.addVar() for a in A for t in time}

# Objective
m.setObjective(quicksum(quicksum(generator[g]["Cost"] * X[g, t] * timePeriodDuration for g in G)
        for t in time), GRB.MINIMIZE)

# Constraints

# Constraint 1: Generator power production is less than its capacity at any time
for t in time:
    for g in G:
        m.addConstr(X[g, t] <= generator[g]['Capacity'])

# Constraint 2: For each substation node, the power in the incoming arcs is equal to the demand
# of the node plus the sum of the power in the outgoing arcs. Input power is multiplied by
# efficiency to account for lost electricity
for t in time:
    for n in nodes:
        # Only substation nodes
        if n['number'] not in generatorNo:
            m.addConstr((quicksum(Y[a['Arc Number'], t] * a['Efficiency'] for a in arcs
                    if a['Node2'] == n['number']) == (n['demand'][t] +
                    quicksum(Y[a['Arc Number'], t] for a in arcs if a['Node1'] == n['number']))))

# Constraint 3: For each generator, the amount of power produced plus the total power from incoming
# arcs is equal to the total power into outgoing arcs
for t in time:
    index = 0  # Index to access each generator
    for g in generator:
        # Set of outflowing arcs from generator
        outflow = []

        # Set of inflowing arcs from generator
        inflow = []

        for a in arcs:
            if a['Node1'] == g['Number']:
                outflow.append(a)
            if a['Node2'] == g['Number']:
                inflow.append(a)

        m.addConstr(quicksum(Y[a['Arc Number'], t] * a['Efficiency'] for a in inflow) +
                X[index, t] == quicksum(Y[p['Arc Number'], t] for p in outflow))
        index += 1

# Constraint 4: For all restricted arcs, the power in each arc is less than or equal to its limit
for t in time:
    for a in A:
        if a not in Unrestricted:
            m.addConstr(Y[a, t] <= powerLimit)

# Constraint 5-9, ensuring that each generator's output should not change more than powerChange MW
# between time periods
for t in time[:-1]:
    for g in G:
        m.addConstr(X[g, t] - X[g, t + 1] <= powerChange)
        m.addConstr(X[g, t + 1] - X[g, t] <= powerChange)

# Model assumes that the first time period being constrained by the last time period of the same
# day, is equivalent to constraining the first time period of the day by the last time period of the
# previous day
for g in G:
    m.addConstr(X[g, 5] - X[g, 0] <= powerChange)
    m.addConstr(X[g, 0] - X[g, 5] <= powerChange)

m.optimize()

print("Objective value: Optimal Total Cost Over The Day = $", m.objVal)
for t in time:
    print("\nGenerator power produced breakdown at time period", t, ":")
    for g in G:
        print("Generator", g, "produces", X[g, t].x, "MW/h")

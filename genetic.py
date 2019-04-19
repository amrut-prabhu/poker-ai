# code modified from https://github.com/ssemenova/Genetic-Poker

from __future__ import division # floating point division instead of integer division, which is the default in python 2
from numpy.random import choice # used to make a weighted random choice for parents
import random # random number generator
import copy # create copy of object
import numpy as np
import Group02PlayerConfig as Group02PlayerConfig
from Group02PlayerConfig import Group02Player
from pypokerengine.api.game import setup_config, start_poker

################## CONSTANTS ##################
# Game characteristics for determining relative fitnesses of players
MAX_GAME_ROUNDS = 30
INITIAL_STACK = 10000
SMALL_BLIND_AMOUNT = 20

# Genetic Algorithm hyperparameters
## NOTE!!!: 
## POPULATION_SIZE should be multiple of 10
## @deprecated PLAYERS_PER_TABLE should be a factor of POPULATION_SIZE

POPULATION_SIZE = 20#200 # Number of chromosomes
GENERATIONS = 50#300 # Number of times that selections occur

PLAYERS_PER_TABLE = 2 #4 
TABLES = POPULATION_SIZE - PLAYERS_PER_TABLE + 1 #int(POPULATION_SIZE / PLAYERS_PER_TABLE)
###############################################

def normalize(narray):
    """
    normalise to percentages
    """
    return narray/sum(narray)

def normalize_list(list):
    return [float(i)/sum(list) for i in list]
    
def main():
    print("----------------Characteristics of Run-------------------------")
    print("Game:")
    print("MAX_GAME_ROUNDS=    " + str(MAX_GAME_ROUNDS))
    print("INITIAL_STACK=      " + str(INITIAL_STACK))
    print("SMALL_BLIND_AMOUNT= " + str(SMALL_BLIND_AMOUNT))
    print("\nGenetic Algo:")
    print("POPULATION_SIZE=    " + str(POPULATION_SIZE))
    print("GENERATIONS=        " + str(GENERATIONS))
    print("\nGroup02Player:")
    print("  MINIMAX_DEPTH=    " + str(Group02PlayerConfig.MINIMAX_DEPTH))
    print("  NUM_ROUNDS=       " + str(Group02PlayerConfig.NUM_ROUNDS))
    print("--------------------------------------------------------------")

    num_parents = int(POPULATION_SIZE / 2)

    # STEP 1: Generate population
    population = []
    for i in range(POPULATION_SIZE):
        population.append(Group02Player())

    # loop through generations
    for gen in range(GENERATIONS):
        # STEP 2: Calculate fitness of each Group02Player and average population fitness
        probabilityList = calculatePopulationFitness(population, POPULATION_SIZE, gen)

        # STEP 3: Select parents for next generation

        # sort in reverse order of fitness
        population.sort(key=lambda hand: hand.fitness, reverse=True)

        # choose parents
        parents = []
        for i in range(num_parents):
            # choose random parent, giving weight to their fitness
            newParent = choice(population, p = probabilityList)
            parents.append(newParent)

        # STEP 4: Reproduce with 80% crossover, 10% mutation, and 10% elitism
        # new population becomes the result of reproduction

        # start with no children
        population = []

        # mutation 15% of the time:
        # creating .1 * POPULATION_SIZE children
        for i in range(int(.2 * POPULATION_SIZE)):
            population.append(mutate(parents))

        # elitism 10% of the time:
        for i in range(int(.1 * POPULATION_SIZE)):
            population.append(elitism(parents))

        # crossover 75%
        for i in range(int(.7 * POPULATION_SIZE)):
            population.append(crossover(parents))

    print("Final generation")
    displayGeneration(gen+1, population)    
    calculatePopulationFitness(population, POPULATION_SIZE, GENERATIONS)

def displayGeneration(genNum, population):
    print("Generation #" + str(genNum) + ":")
    for player in population:
        print(player.__str__()) 

def calculatePopulationFitness(population, populationSize, gen):
    """
    Calculate the fitness of each Group02Player in the population
    Calculate and print average fitness of the population
    Determine and print the Group02Player that has the maximum fitness
    """
    max_fitness = -float("inf") # maximum fitness of a Group02Player
    max_fitness_player = population[0] # Group02Player that has the maximum fitness
    odds_list = [] # list of probabilities associated with a Group02Player .. needed to make the choice of parents

    # total_fitness = [0] * populationSize

    # Create a random order of players
    order = np.random.permutation(populationSize)
    for table in range(TABLES):

        # Calculate fitnesses for the players in this table round
        players = [(population[i], i) for i in order[table : table+PLAYERS_PER_TABLE]]
        players, probabilities = play_round(players)

        for num in players:
            old_fitness = population[num].get_fitness()
            
            if old_fitness == -1 or table == 0:
                new_fitness = probabilities[players.index(num)]
            else:
                new_fitness = (old_fitness + probabilities[players.index(num)])/2

            population[num].set_fitness(new_fitness)

        # Add the table's probabilities to the total list
        if table == 0:
            odds_list.extend(probabilities)
        else:
            odds_list.pop()
            odds_list.extend(probabilities)

        # Update max fitness if max of current round is higher 
        round_max_fitness = max(probabilities)
        if (round_max_fitness > max_fitness):
            max_fitness = round_max_fitness
            max_fitness_player = players[probabilities.index(round_max_fitness)]

    # scaling probabilities so they all add up to one
    probability_list = normalize_list(odds_list)
    probability_list.sort(reverse=True)

    total_fitness = sum(odds_list)
    print("Generation #" + str(gen) + ":")
    print("    Mean fitness Score = " + str(total_fitness / populationSize))
    print("    Max fitness is " + population[max_fitness_player].__str__())
    print

    return probability_list

def play_round(players):
    """
    Input:
        players: a list of PLAYERS_PER_TABLE tuples- (player, num) where num is the index of player in population
    Output:
        - order of the players
        - their corresponding payoff probabilities
    """
    config = setup_config(max_round=MAX_GAME_ROUNDS, initial_stack=INITIAL_STACK, small_blind_amount=SMALL_BLIND_AMOUNT)
    # print("Setting up a new game")

    for player, num in players:
        config.register_player(name=num, algorithm=player)

    results = start_poker(config, verbose=0)
    # print("The final results of the poker game are: ", results)

    playerOrder = []
    fitnesses = []

    for player in results['players']:
        playerOrder.append(player['name'])
        fitnesses.append(player['stack'])

    return playerOrder, normalize_list(fitnesses)

# mutates a child from a random parent
def mutate(parents):
    # pick random parent
    parent = parents[random.randrange(0, len(parents))]
    # copy parent's information to the child
    child = copy.deepcopy(parent)
    # mutate the child
    child.mutate()
    return child

# creates a child that is a clone of the parent
def elitism(parents):
    # pick random parent
    parent = parents[random.randrange(0, len(parents))]
    # copy parent's information to child
    child = copy.deepcopy(parent)
    return child

# creates a child that is a combination of both parents
def crossover(parents):
    # pick two random parents
    j = random.randrange(0, len(parents)//2 + 1)
    parent1 = parents[j] # First parent is randomly chosen from the first half (fittest parents)
    parent2 = parents[random.randrange(0, len(parents))]

    index = random.randrange(0,3)
    new_weights = []

    for i in range(index):
        new_weights.append(parent1.weights[i])

    for i in range(3-index):
        new_weights.append(parent2.weights[i])

    child = Group02Player(normalize(np.array(new_weights)))
    
    return child

main()
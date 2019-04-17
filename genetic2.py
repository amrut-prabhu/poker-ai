from __future__ import division # floating point division instead of integer division, which is the default in python 2
from numpy.random import choice # used to make a weighted random choice for parents
import random # random number generator
import copy # create copy of object
import numpy as np
from MiniMaxPlayer import MiniMaxPlayer
from pypokerengine.api.game import setup_config, start_poker

def normalize(narray):
    """
    normalise to percentages
    """
    return narray/sum(narray)

def normalize_list(list):
    return [float(i)/sum(list) for i in list]

################## CONSTANTS ##################
# Game characteristics
MAX_GAME_ROUNDS = 5#10
INITIAL_STACK = 1000
SMALL_BLIND_AMOUNT = 10

# Genetic Algorithm hyperparameters
## NOTE!!!!!: 
## POPULATION_SIZE should be multiple of 10
## PLAYERS_PER_TABLE should be a factor of POPULATION_SIZE

POPULATION_SIZE = 10#200 # Number of chromosomes
GENERATIONS = 5#300 # Number of times that selections occur

PLAYERS_PER_TABLE = 2#4 
TABLES = int(POPULATION_SIZE / PLAYERS_PER_TABLE)
###############################################

def main():
    num_parents = int(POPULATION_SIZE / 2)

    # STEP 1: Generate population
    population = []
    for i in range(POPULATION_SIZE):
        population.append(MiniMaxPlayer())

    # loop through generations
    for gen in range(GENERATIONS):
        # STEP 2: Calculate fitness of each MiniMaxPlayer and average population fitness
        probabilityList = calculatePopulationFitness(population, POPULATION_SIZE, gen)

        # STEP 3: Select parents for next generation

        # sort in reverse order of fitness
        population.sort(key=lambda hand: hand.fitness, reverse=True)

        for player in population:
            print(player.__str__()) 

        # choose parents
        parents = []
        for i in range(num_parents):
            # choose random parent, giving weight to their fitness
            newParent = choice(population, p = probabilityList)
            parents.append(newParent)

        # STEP 4: Reproduce with 80% crossover, 10% mutation, and 10% elitism
        # new population becomes the result of reproduction

        # print("Init size: " + str(len(population)))

        # start with no children
        population = []

        # mutation 10% of the time:
        # creating .1 * POPULATION_SIZE children
        for i in range(int(.1 * POPULATION_SIZE)):
            population.append(mutate(parents))

        # elitism 10% of the time:
        for i in range(int(.1 * POPULATION_SIZE)):
            population.append(elitism(parents))

        # crossover 80%
        for i in range(int(.8 * POPULATION_SIZE)):
            population.append(crossover(parents))

        # print("Final size: " + str(len(population)))

    print("Final generation")
    calculatePopulationFitness(population, POPULATION_SIZE, GENERATIONS)

def calculatePopulationFitness(population, populationSize, gen):
    """
    Calculate the fitness of each MiniMaxPlayer in the population
    Calculate and print average fitness of the population
    Determine and print the MiniMaxPlayer that has the maximum fitness
    """
    max_fitness = -float("inf") # maximum fitness of a MiniMaxPlayer
    max_fitness_player = population[0] # MiniMaxPlayer that has the maximum fitness
    odds_list = [] # list of probabilities associated with a MiniMaxPlayer .. needed to make the choice of parents

    # Divide all the players to play in tables of 4.
    total_fitness = [0] * populationSize

    # Create a random order of players
    order = np.random.permutation(populationSize)
    for table in range(TABLES):
        # print("Beginning population round {0}".format(round))

        # print(len(population))
        # print(len(order))
        # print(table*PLAYERS_PER_TABLE)
        # print(table*PLAYERS_PER_TABLE+PLAYERS_PER_TABLE)

        # Calculate fitnesses for the players in this round
        players = [(population[i], i) for i in order[table*PLAYERS_PER_TABLE : table*PLAYERS_PER_TABLE+PLAYERS_PER_TABLE]]
        players, probabilities = play_round(players)

        # print(probabilities)
        for idx in players:
            population[idx].set_fitness(probabilities[players.index(idx)])
            # print(population[idx].__str__()) 

        # Add the table's probabilities to the total list
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
    print('Fitness Score for Generation #' + str(gen) + ' = ' + str(total_fitness / populationSize))
    print('    Maximum fitness is ' + str(max_fitness) + " for the player " + max_fitness_player.__str__())

    return probability_list

def play_round(players):
    """
    Input:
        players: a list tuples- (player, num) where num is the index of player in population
    Output:
        a list of the players' payoff probabilities
    """
    config = setup_config(max_round=MAX_GAME_ROUNDS, initial_stack=INITIAL_STACK, small_blind_amount=SMALL_BLIND_AMOUNT)
    # print("Setting up a new game")

    for player, num in players:
        # print("Registering player {0}".format(num))
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
    # print(len(parents)//2)
    # print(j)
    parent1 = parents[j] # First parent is randomly chosen from the first half (fittest parents)
    parent2 = parents[random.randrange(0, len(parents))]

    index = random.randrange(0,3)
    new_weights = []

    for i in range(index):
        new_weights.append(parent1.weights[i])

    for i in range(3-index):
        new_weights.append(parent2.weights[i])

    child = MiniMaxPlayer(normalize(np.array(new_weights)))
    
    return child

main()
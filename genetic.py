## A genetic algorithm for finding optimal weights for the MiniMaxPlayer heuristics
from pypokerengine.api.game import setup_config, start_poker
from MiniMaxPlayer import MiniMaxPlayer
import numpy as np

"""
Weights of each of the heuristics
"""
init_def_weights = np.array([0.4, 0.3, 0.3])

def normalize(narray):
    """
    normalise to percentages
    """
    return [narray/sum(narray)]

def add_all(list_of_lists):
    """
    Adds a list of lists togther
    """
    result = []
    for i in range(len(list_of_lists[0])):
        result.append(sum([lst[i] for lst in list_of_lists]))
    return result


class Population(object):
    def __init__(self, size):
        self.pop = []
        self.size = size
        for i in range(size):
			# generate a random bot
            def_weights = normalize(init_def_weights * (1 + np.random.uniform(-0.25, 0.25, size=(1,3))))
            self.pop.append(MiniMaxPlayer(def_weights))

    def birth_cycle(self):
        """ Conduct a full Moran process, storing the relative fitnesses in a file """
        fitnesses = np.sqrt(self.compute_fitness())
        fitnesses = normalize(fitnesses)

        new_generation = list(np.random.choice(self.pop, self.size/2, p=fitnesses, replace=False)) #these are the survivors of the Moran process.
		
        births = np.random.choice(self.pop, self.size - self.size/2, p=fitnesses, replace=True) #these are the new additions
		
        for new_ai in births:
            # Create mutations in chromosomes at uniform random 
            if np.random.uniform(0,1) > 0.75:
                new_ai.mutate()
            new_generation.append(new_ai)
        self.pop = new_generation

        print("New generation created!")
        self.printWeights()

    def compute_fitness(self):
        # Divide all the players into 4 tables to play. Play a total of 5 rounds
        total_fitness = [0] * self.size

        for round in range(5):
            print("Beginning population round {0}".format(round))
            tables = np.random.permutation(self.size)
            
            table1 = [(self.pop[i], i) for i in tables[:self.size//4]]
            table2 = [(self.pop[i], i) for i in tables[self.size//4:2*self.size//4]]
            table3 = [(self.pop[i], i) for i in tables[2*self.size//4:3*self.size//4]]
            table4 = [(self.pop[i], i) for i in tables[3*self.size//4:]]
            
            round_fitness = add_all([self.play_round(table1), self.play_round(table2), self.play_round(table3), self.play_round(table4)])
            print("The fitness totals for this round are: ", round_fitness)
            
            total_fitness = add_all([round_fitness, total_fitness])
        return total_fitness

    def play_round(self, players):
        """
        Input: 
            players: a list of 2 tuples- (player, num) where num is the index of player in self.pop
        Output: 
            a list of the 2 players' payoffs
        """
        # if (len(players) != 2):
            # raise ValueError('The genetic algo fitness game has more than 2 players.')

        config = setup_config(max_round=20, initial_stack=1000, small_blind_amount=10)
        print("Setting up a new game")

        for player, num in players:
            print("Registering player {0}".format(num))
            config.register_player(name=num, algorithm=player)

        results = start_poker(config, verbose=0)
        print("The final result of the poker game is: ", results)

        fitnesses = [0] * self.size
        for player in results['players']:
            fitnesses[player['name']] = player['stack']
        
        return fitnesses

    def printWeights(self):
        print([(p.default_weights) for p in self.pop])
        save_file = open("population.txt", "a+")
        save_file.write(str([(p.default_weights) for p in self.pop]))


POPULATION_SIZE = 10 # Number of chromosomes
NUM_EPOCHS = 5 # Number of times that selections occur

population = Population(POPULATION_SIZE)
population.printWeights()
for epoch in range(NUM_EPOCHS):
	print("Running epoch {0}".format(epoch))
	population.birth_cycle()

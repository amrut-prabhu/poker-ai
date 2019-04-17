from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.emulator import Emulator
from pypokerengine.engine.card import Card
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate
from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card, attach_hole_card_from_deck
import numpy as np
import time

def normalize(narray):
    """
    normalise to percentages
    """
    return narray/sum(narray)

class MiniMaxPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    def __init__(self, def_weights = None):
        """
        Input: Hyperparameters that govern play

               Heuristic weights (size = 3) for:
                1. win rate
                2. money in pot
                3. opponent modelling
        """
        BasePokerPlayer.__init__(self)

        self.fitness = -1
        init_starting_weights = np.array([105,0.03,0])
        if def_weights is None:
            self.weights = normalize(init_starting_weights * (1 + np.random.uniform(-0.25, 0.25, size=3)))
        else:
            self.weights = def_weights

    def __str__(self):
        return str("P weights: " + str([round(float(i), 6) for i in self.weights]) + " fitness: " + str(self.fitness))

    def set_fitness(self, fit):
        self.fitness = fit

    def mutate(self):
        """
        Mutate and change form!
        """
        self.weights = normalize(self.weights * (1 + np.random.uniform(-0.3, 0.3, size=3)))

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        x = time.time()
        num_rounds = 35
        uuid = 0
        for p in round_state['seats']:
            if (p['name'] == 'MiniMaxPlayer'):
                uuid = p['uuid']

        cards = list(map(lambda x: Card.from_str(x), hole_card))
        player = round_state['next_player']
        game_state = get_game_state(round_state, cards, uuid)
        game = Game(cards,player,game_state, num_rounds, valid_actions,round_state, self.weights)
        action = game.minimax(game_state, 3)
        #print("FINAL ACTION: "+str(valid_actions[index]))
        #call_action_info = valid_actions[index]
        #action = call_action_info["action"]
        # print("WHAT AM I DOING: "+action)
        # print(time.time() - x)
        return action

    def receive_game_start_message(self, game_info):
        pass
        #print("THIS IS THE GAME INFO: "+ str(game_info))

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        #print(str(street)+" "+str(round_state))
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
        #print(str(winners)+" "+str(hand_info))


def get_game_state(round_state, hole_card, uuid):
    game_state = restore_game_state(round_state)
    for player_info in round_state['seats']:
        uuid_new = player_info['uuid']
        if uuid_new == uuid:
            game_state = attach_hole_card(game_state, uuid, hole_card)
        else:
            game_state = attach_hole_card_from_deck(game_state, uuid_new)

    return game_state


class Game:
    def __init__(self, hole_card, player, state, num_rounds, valid_actions, round_state, weights):
        self.hole_card = hole_card
        self.player = player
        self.init_state = state
        self.emulator = Emulator()
        self.num_rounds = num_rounds
        self.valid_actions = valid_actions
        self.weights = weights
        self.round_state = round_state
        self.emulator.set_game_rule(2,self.num_rounds,10,0)

    """ Check if game tree ends """
    def terminal_test(self,state):
        return self.emulator._is_last_round(state, self.emulator.game_rule)

    """ generate legal moves at this state """
    def actions(self,state):
        temp = list(map(lambda x:x['action'],self.emulator.generate_possible_actions(state)))
        return temp

    def eval_heuristics(self, player, state):
        win_rate = estimate_hole_card_win_rate(self.num_rounds, 2, self.hole_card, state['table']._community_card)
        amount_in_pot = self.round_state['pot']['main']['amount']

        heuristics = [win_rate, amount_in_pot, 1]
        res =np.dot(self.weights, heuristics)
        #print("DEBUG DEBUG DEBUG: "+str(res))
        return res

    def future_move(self, state):
        return state['next_player']

    """ projects what happens when making a move from current state """
    def project (self, curr_state, move):
        return self.emulator.apply_action(curr_state, move)[0]

    """ TODO: Change to expectimax when stuff works """
    def minimax(self, newState, max_depth):

        player = self.future_move(newState)
        inf = float('inf')

        def min_value(newState,alpha,beta,depth):
            if depth== max_depth or self.terminal_test(newState):
            #if self.terminal_test(newState):
                return self.eval_heuristics(player, newState)
            v = inf
            for a in self.actions(newState):
                v = min(max_value(self.project(newState, a),alpha,beta, depth+1),v)
                if v<=alpha:
                    return v
                beta = min(beta,v)
            return v

        def max_value(newState,alpha,beta,depth):
            if depth == max_depth or self.terminal_test(newState):
            #if self.terminal_test(newState):
                return self.eval_heuristics(player, newState)
            v = -inf
            for a in self.actions(newState):
                v = max(min_value(self.project(newState, a), alpha,beta, depth+1),v)
                if (v>=beta):
                    return v
                alpha = max(alpha,v)
            return v

        best_score = -inf
        beta = inf
        best_action = None
        for a in self.actions(newState):
            v = min_value(self.project(newState, a), best_score, beta,0)
            if v > best_score:
                best_score = v
                best_action = a
                #print("RES"+str(best_action))
        return best_action

        #a = np.argmax(list(map(lambda a: min_value(self.project(newState, a),0),self.actions(newState))))


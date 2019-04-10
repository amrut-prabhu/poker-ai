from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.emulator import Emulator
from pypokerengine.engine.card import Card
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate
from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card, attach_hole_card_from_deck
import numpy as np

class MiniMaxPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    def __init__(self, def_weights):
        """
        Input: Hyperparameters that govern play
        """
        self.default_weights = def_weights

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        num_rounds = 100
        for p in round_state['seats']:
            if (p['name'] == 'MiniMaxPlayer'):
                uuid = p['uuid']

        cards = list(map(lambda x: Card.from_str(x), hole_card))
        player = round_state['next_player']
        game_state = get_game_state(round_state, cards, uuid)
        game = Game(cards, player, game_state, num_rounds, valid_actions, round_state)
        index = game.minimax(game_state,1)
        #print("FINAL ACTION: "+str(valid_actions[index]))
        call_action_info = valid_actions[index]
        action = call_action_info["action"]
        # print("WHAT I AM DOING: "+action)
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
    def __init__(self, hole_card, player, state, num_rounds, valid_actions, round_state):
        self.hole_card = hole_card
        self.player = player
        self.init_state = state
        self.emulator = Emulator()
        self.num_rounds = num_rounds
        self.valid_actions = valid_actions
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
        if (self.player == player):
            return win_rate, amount_in_pot
        return -win_rate, amount_in_pot

    def future_move(self, state):
        return state['next_player']

    """ projects what happens when making a move from current state """
    def project (self, curr_state, move):
        return self.emulator.apply_action(curr_state, move)[0]

    """ TODO: Change to expectimax when stuff works """
    def minimax(self, newState, max_depth):

        player = self.future_move(newState)
        inf = float('inf')

        def min_value(newState, depth):
            if depth== max_depth or self.terminal_test(newState):
                return self.eval_heuristics(player, newState)
            v = inf
            for a in self.actions(newState):
                v = min(max_value(self.project(newState, a),depth+1),v)
            return v

        def max_value(newState, depth):
            if depth == max_depth or self.terminal_test(newState):
                return self.eval_heuristics(player, newState)
            v = -inf
            for a in self.actions(newState):
                v = max(min_value(self.project(newState, a), depth+1),v)

            return v

        return np.argmax(list(map(lambda a: min_value(self.project(newState, a),0),self.actions(newState))))


# from pypokerengine.players import BasePokerPlayer
# from pypokerengine.api.game import setup_config, start_poker
# from pypokerengine.utils.card_utils import gen_cards, _montecarlo_simulation, estimate_hole_card_win_rate
# import numpy as np

# def normalize(narray):
# 	return [narray/sum(narray)]

# class MiniMaxPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

#     def __init__(self, def_weights):
#         """
#         Input: Hyperparameters that govern play
#         """
#         self.default_weights = def_weights

#     # def print(self):
#     #     print(self.default_weights)

#     def mutate(self):
#         """
#         Mutate and change form!
#         """
#         self.default_weights = normalize(self.default_weights * (1 + np.random.uniform(-0.25, 0.25, size=(1,3))))
        
#     #  we define the logic to make an action through this method. (so this method would be the core of your AI)
#     def declare_action(self, valid_actions, hole_card, round_state):
#         nb_simulations = 1000
#         # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
#         heuristics_score = evaluate_heuristics(num_simulations,hole_card,round_state['community_card'])
#         call_action_info = valid_actions[1]
#         #action, amount = call_action_info["action"], call_action_info["amount"]
#         #return action, amount   # action returned here is sent to the poker engine
#         action = call_action_info["action"]

#         return action

#     def evaluate_heuristics(num_simulations,hole_card,community_card=None):
#         #always between 0 to 1
#         win_rate = estimate_hole_card_win_rate(num_simulations, 2, gen_cards(hole_card), gen_cards(community_card)
#         items = [item for item in valid_actions if item['action'] == action]
#         amount = items[0]['amount']
#         return win_rate , amount

#     def receive_game_start_message(self, game_info):
#         pass

#     def receive_round_start_message(self, round_count, hole_card, seats):
#         pass

#     def receive_street_start_message(self, street, round_state):
#         pass

#     def receive_game_update_message(self, action, round_state):
#         pass

#     def receive_round_result_message(self, winners, hand_info, round_state):
#         pass


# # Setup game
# config = setup_config(max_round=10, initial_stack=1000, small_blind_amount=10)

# init_def_weights = np.array([0.4, 0.3, 0.3])
# config.register_player(name="p1", algorithm=MiniMaxPlayer(init_def_weights))
# config.register_player(name="p2", algorithm=MiniMaxPlayer(init_def_weights))
# game_result = start_poker(config, verbose=1)

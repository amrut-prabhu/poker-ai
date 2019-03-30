from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.utils.card_utils import gen_cards, _montecarlo_simulation, estimate_hole_card_win_rate
class MiniMaxPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        nb_simulations = 1000
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        heuristics_score = evaluate_heuristics(num_simulations,hole_card,round_state['community_card'])
        call_action_info = valid_actions[1]
        #action, amount = call_action_info["action"], call_action_info["amount"]
        #return action, amount   # action returned here is sent to the poker engine
        action = call_action_info["action"]

        return action

    def evaluate_heuristics(num_simulations,hole_card,community_card=None):
        #always between 0 to 1
        win_rate = estimate_hole_card_win_rate(num_simulations, 2, gen_cards(hole_card), gen_cards(community_card)
        items = [item for item in valid_actions if item['action'] == action]
        amount = items[0]['amount']
        return win_rate , amount

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

config = setup_config(max_round=10, initial_stack=100, small_blind_amount=10)
config.register_player(name="p1", algorithm=MiniMaxPlayer())
config.register_player(name="p2", algorithm=MiniMaxPlayer())
game_result = start_poker(config, verbose=1)

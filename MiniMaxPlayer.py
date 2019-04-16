from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.emulator import Emulator
from pypokerengine.engine.card import Card
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate
from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card, attach_hole_card_from_deck
from pypokerengine.engine.hand_evaluator import HandEvaluator
import numpy as np
import time

def normalize(narray):
    """
    normalise to percentages
    """
    return narray/sum(narray)

# Preflop income rates for 1 active opponent. Obtained via simulation (view Loki paper for info)
IR2_2 = [7, -351, -334, -314, -318, -308, -264, -217, -166, -113, -53, 10, 98]
IR2_3 = [-279, 74, -296, -274, -277, -267, -251, -201, -148, -93, -35, 27, 116]
IR2_4 = [-263, -225, 142, -236, -240, -231, -209, -185, -130, -75, -17, 46, 134]
IR2_5 = [-244, -206, -169, 207, -201, -189, -169, -148, -114, -55, 2, 68, 153]
IR2_6 = [-247, -208, -171, -138, 264, -153, -134, -108, -78, -43, 19, 85, 154]
IR2_7 = [-236, -200, -162, -125, -91, 324, -99, -72, -43, -6, 37, 104, 176]
IR2_8 = [-192, -182, -143, -108, -75, -43, 384, -39, -4, 29, 72, 120, 197]
IR2_9 = [-152, -134, -122, -84, -50, -17, 16, 440, 28, 65, 106, 155, 215]
IR2_10 = [-104, -86, -69, -56, -19, 12, 47, 81, 499, 102, 146, 195, 254]
IR2_J = [-52, -35, -19, 0, 11, 46, 79, 113, 149, 549, 161, 212, 271]
IR2_Q = [2, 21, 34, 55, 72, 86, 121, 153, 188, 204, 598, 228, 289]
IR2_K = [63, 79, 98, 116, 132, 151, 168, 200, 235, 249, 268, 647, 305]
IR2_A = [146, 164, 180, 198, 198, 220, 240, 257, 291, 305, 323, 339, 704]
IR2 = [IR2_2, IR2_3, IR2_4, IR2_5, IR2_6, IR2_7, IR2_8, IR2_9, IR2_10, IR2_J, IR2_Q, IR2_K, IR2_A]

def HandStrength(weight, hole_card, community_card):
    ahead = tied = behind = 0
    ourrank = HandEvaluator.eval_hand(hole_card, community_card)
    # Consider all two card combinations of the remaining cards.
    unused_cards = _pick_unused_card(2, hole_card + community_card)
    oppcards = [unused_cards[2*i:2*i+2] for i in range(1)]
    for oppcard in oppcards:
        # initial opponent hand value
        opprank = HandEvaluator.eval_hand(oppcard, community_card)
        # enemy card weight
        oppweight = HandRanker.Map_169(oppcard[0], oppcard[1], weight)
        if(ourrank>opprank): ahead += oppweight
        elif (ourrank==opprank): tied += oppweight
        else: behind += oppweight # <
    handstrength = (ahead+tied/2)/(ahead+tied+behind)
    return handstrength

def HandPotential(weight, hole_card, community_card):
    ahead = 0
    tied = 1
    behind = 2
    # Hand potential array, each index represents ahead, tied, and behind.
    HP = [[0 for x in range(3)] for y in range(3)] # initialize to 0 
    HPTotal = [0 for x in range(3)] # initialize to 0 
    ourrank = HandEvaluator.eval_hand(hole_card, community_card)
    # Consider all two card combinations of the remaining cards for the opponent.
    unused_cards = _pick_unused_card(2, hole_card + community_card)
    oppcards = [unused_cards[2*i:2*i+2] for i in range(1)]
    for oppcard in oppcards:
        # initial opponent hand value
        opprank = HandEvaluator.eval_hand(oppcard, community_card)
        # enemy card weight
        oppweight = HandRanker.Map_169(oppcard[0], oppcard[1], weight)
        if(ourrank>opprank): index = ahead
        elif(ourrank==opprank): index = tied
        else: index = behind # < 
        HPTotal[index] += oppweight
        unused_cards_postflop = _pick_unused_card(2, hole_card + community_card + oppcard)
        turn = unused_cards_postflop[0]
        unused_cards_postturn = _pick_unused_card(2, hole_card + community_card + oppcard + turn)
        river = unused_cards_postturn[0]
        # All possible board cards to come. 
        for turn_card in turn:
            for river_card in river:
                # Final 5-card board 
                board = community_card+turn+river
                ourbest = HandEvaluator.eval_hand(hole_card,board)
                oppbest = HandEvaluator.eval_hand(oppcard,board)
                if(ourbest>oppbest): HP[index][ahead] +=oppweight
                elif(ourbest==oppbest): HP[index][tied] +=oppweight
                else: HP[index][behind] +=oppweight # <
    sumBehind = HP[behind][ahead] + HP[behind][tied] + HP[behind][behind] 
    sumTied = HP[tied][ahead] + HP[tied][tied] + HP[tied][behind]
    sumAhead = HP[ahead][ahead] + HP[ahead][tied] + HP[ahead][behind]
    # Ppot: were behind but moved ahead. 
    Ppot = (HP[behind][ahead]+HP[behind][tied]/2+HP[tied][ahead]/2)/ (sumBehind+sumTied/2)
    # Npot: were ahead but fell behind. 
    Npot = (HP[ahead][behind]+HP[tied][behind]/2+HP[ahead][tied]/2)/ (sumAhead+sumTied/2)
    printStats(HPTotal, HP)
    return Ppot

def EffectiveHandStrength(oppcards, boardcards):
    weight = IR2
    HS = HandStrength(weight, oppcards, boardcards)
    Ppot = HandPotential(weight, oppcards, boardcards)
    return (HS + (1 - HS)*Ppot)

# Debug
def printStats(HPTotal, HP):
    ahead = 0
    tied = 1
    behind = 2
    sumBehind = HP[behind][ahead] + HP[behind][tied] + HP[behind][behind] 
    sumTied = HP[tied][ahead] + HP[tied][tied] + HP[tied][behind]
    sumAhead = HP[ahead][ahead] + HP[ahead][tied] + HP[ahead][behind]
    print("Handstrength (current board):")
    print("Ahead weighted sum: " + HPTotal[ahead])
    print("Behind weighted sum: " + HPTotal[behind])
    print("Tied weighted sum: " + HPTotal[tied])
    hs = (HPTotal[ahead]+HPTotal[tied]/2) / (HPTotal[ahead]+HPTotal[behind]+HPTotal[tied])
    print("Handstrength one opponent: " + hs)
            
    print("TRANSITIONS (currently ahead)")
    print("Total simulations sarting ahead: " + sumAhead)
    print("Ahead-Ahead: " + HP[ahead][ahead])
    print("Ahead-Tied: " + HP[ahead][tied])
    print("Ahead-Behind: " + HP[ahead][behind])
            
    print("TRANSITIONS (currently behind)")
    print("Total simulations sarting behind: " + sumBehind)
    print("Behind-Ahead: " + HP[behind][ahead])
    print("Behind-Tied: " + HP[behind][tied])
    print("Behind-Behind" + HP[behind][behind])
        
    print("TRANSITIONS (currently tied)")
    print("Total simulations sarting tied: " + sumTied)
    print("Tied-Ahead: " + HP[tied][ahead])
    print("Tied-Tied: " + HP[tied][tied])
    print("Tied-Behind: "+ HP[tied][behind])

class MiniMaxPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    def __init__(self):
        """
        Input: Hyperparameters that govern play
               
               Heuristic weights (size = 3) for:
                1. win rate
                2. money in pot
                3. opponent modelling 
        """
        BasePokerPlayer.__init__(self)
        #self.default_weights = def_weights

    def mutate(self):
        """
        Mutate and change form!
        """
        self.default_weights = normalize(self.default_weights * (1 + np.random.uniform(-0.25, 0.25, size=3)))

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
        game = Game(cards,player,game_state, num_rounds, valid_actions,round_state, self.default_weights)
        index = game.minimax(game_state, 1)
        #print("FINAL ACTION: "+str(valid_actions[index]))
        call_action_info = valid_actions[index]
        action = call_action_info["action"]
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
        EHS = EffectiveHandStrength(self.hole_card, state['table']._community_card)

        heuristics = [win_rate, amount_in_pot, EHS]
        return np.dot(self.weights, heuristics)

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

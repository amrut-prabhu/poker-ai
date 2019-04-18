from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.emulator import Emulator
from pypokerengine.engine.card import Card
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate, _pick_unused_card, _fill_community_card
from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card, attach_hole_card_from_deck
from pypokerengine.engine.hand_evaluator import HandEvaluator
import numpy as np
import time
import random

MINIMAX_DEPTH = 2
NUM_ROUNDS = 25 # num rounds in MiniMax Game?

isDebug = False
isActionTimed = False # either enable isActionTimed or isHeuristicTimed? (not both together?)
isHeuristicTimed = False 


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

cardRankToStartIndex = {2:0,3:1,4:2,5:3,6:4,7:5,8:6,9:7,10:8,11:9,12:10,13:11,14:12}

cardSuitToStartIndex = {2:0,4:1,8:2,16:3}

def Map_169(c1, c2, toMap):
    rank1 = c1.rank
    rank2 = c2.rank
    idx1 = cardRankToStartIndex[rank1]
    idx2 = cardRankToStartIndex[rank2]

    r1Greatest = rank1 > rank2
    if(c1.suit == c2.suit):
        return toMap[idx1][idx2] if r1Greatest else toMap[idx2][idx1]
    else:
        return toMap[idx2][idx1] if r1Greatest else toMap[idx1][idx2]

def HandStrength(weight, hole_card, community_card):
    No_of_times = 5 # numround = 35 - 3 for running alone without timeout, 2 for running together
    Ahead = Tied = Behind = 1
    ourrank = HandEvaluator.eval_hand(hole_card, community_card)
    # Consider all two card combinations of the remaining cards.
    unused_cards = _pick_unused_card(45, hole_card + community_card)

    while(No_of_times>0):
        oppcard1 = random.choice(unused_cards)
        oppcard2 = random.choice(unused_cards)
        if(oppcard1 != oppcard2):
            # initial opponent hand value
            oppcard = [oppcard1, oppcard2]
            opprank = HandEvaluator.eval_hand(oppcard, community_card)
            # enemy card weight
            oppweight = (Map_169(oppcard1, oppcard2, weight)/3364.0)
            # print(ourrank, opprank, oppweight)
            if(ourrank>opprank): Ahead += oppweight
            elif (ourrank==opprank): Tied += oppweight
            else: Behind += oppweight # <
            No_of_times = No_of_times - 1
    """
    for oppcard1 in unused_cards:
        for oppcard2 in unused_cards:
            if(oppcard1 != oppcard2):
                # initial opponent hand value
                oppcard = [oppcard1, oppcard2]
                opprank = HandEvaluator.eval_hand(oppcard, community_card)
                # enemy card weight
                oppweight = (Map_169(oppcard1, oppcard2, weight)/3364.0)
                # print(ourrank, opprank, oppweight)
                if(ourrank>opprank): Ahead += oppweight
                elif (ourrank==opprank): Tied += oppweight
                else: Behind += oppweight # <
                No_of_times = No_of_times - 1
    oppcards = [unused_cards[2*i:2*i+2] for i in range(1)]
    """
    handstrength = (Ahead+Tied/2)/(Ahead+Tied+Behind)
    return handstrength

def HandPotential(weight, hole_card, community_card):
    ahead = 0
    tied = 1
    behind = 2
    No_of_times = 5 # numround = 35 - 2 very good for running alone and together without timeout but 3 has few
    # Hand potential array, each index represents ahead, tied, and behind.
    HP = [[1 for x in range(3)] for y in range(3)] # initialize to 0 
    HPTotal = [0 for x in range(3)] # initialize to 0 
    ourrank = HandEvaluator.eval_hand(hole_card, community_card)
    # Consider all two card combinations of the remaining cards for the opponent.
    community_card = _fill_community_card(community_card, used_card=hole_card+community_card)
    unused_cards = _pick_unused_card(45, hole_card + community_card)
    while(No_of_times>0):
        oppcard1 = random.choice(unused_cards)
        oppcard2 = random.choice(unused_cards)
        turn = random.choice(unused_cards)
        river = random.choice(unused_cards)
        if(oppcard1 != oppcard2 != turn != river):
            # initial opponent hand value
            oppcard = [oppcard1, oppcard2]
            opprank = HandEvaluator.eval_hand(oppcard, community_card)
            # enemy card weight
            oppweight = (Map_169(oppcard1, oppcard2, weight)/3364.0)
            if(ourrank>opprank): index = ahead
            elif(ourrank==opprank): index = tied
            else: index = behind # < 
            HPTotal[index] += oppweight
            # Final 5-card board 
            board = community_card
            board.append(turn)
            board.append(river)
            ourbest = HandEvaluator.eval_hand(hole_card,board)
            oppbest = HandEvaluator.eval_hand(oppcard,board)
            if(ourbest>oppbest): HP[index][ahead] +=oppweight
            elif(ourbest==oppbest): HP[index][tied] +=oppweight
            else: HP[index][behind] +=oppweight # <
            No_of_times = No_of_times - 1
    """
    oppcards = [unused_cards[2*i:2*i+2] for i in range(1)]
    for oppcard in oppcards:
        # initial opponent hand value
        opprank = HandEvaluator.eval_hand(oppcard, community_card)
        # enemy card weight
        oppweight = Map_169(oppcard[0], oppcard[1], weight)
        if(ourrank>opprank): index = ahead
        elif(ourrank==opprank): index = tied
        else: index = behind # < 
        HPTotal[index] += oppweight
        hand = hole_card + community_card
        #community_card = _fill_community_card(community_card, used_card=hand.append(oppcard))
        #hand = hand.append(oppcard)
        new_unused_cards = _pick_unused_card(2, hand)
        other_cards = [new_unused_cards[2*i:2*i+2] for i in range(1)]
        # All possible board cards to come. 
        for turn_and_river in other_cards:
            # Final 5-card board 
            board = community_card + turn_and_river
            ourbest = HandEvaluator.eval_hand(hole_card,board)
            oppbest = HandEvaluator.eval_hand(oppcard,board)
            if(ourbest>oppbest): HP[index][ahead] +=oppweight
            elif(ourbest==oppbest): HP[index][tied] +=oppweight
            else: HP[index][behind] +=oppweight # <
    """
    sumBehind = HP[behind][ahead] + HP[behind][tied] + HP[behind][behind] 
    sumTied = HP[tied][ahead] + HP[tied][tied] + HP[tied][behind]
    sumAhead = HP[ahead][ahead] + HP[ahead][tied] + HP[ahead][behind]
    # Ppot: were behind but moved ahead. 
    Ppot = (HP[behind][ahead]+HP[behind][tied]/2+HP[tied][ahead]/2)/ (sumBehind+sumTied/2)
    # Npot: were ahead but fell behind. 
    # Npot = (HP[ahead][behind]+HP[tied][behind]/2+HP[ahead][tied]/2)/ (sumAhead+sumTied/2)
    # printStats(HPTotal, HP)
    return Ppot

def EffectiveHandStrength(oppcards, boardcards):
    weight = IR2
    HS = HandStrength(weight, oppcards, boardcards)
    Ppot = HandPotential(weight, oppcards, boardcards)
    EHS = (HS + (1 - HS)*Ppot)
    #print(HS, Ppot, EHS)
    return EHS

# Debug
def printStats(HPTotal, HP):
    ahead = 0
    tied = 1
    behind = 2
    sumBehind = HP[behind][ahead] + HP[behind][tied] + HP[behind][behind] 
    sumTied = HP[tied][ahead] + HP[tied][tied] + HP[tied][behind]
    sumAhead = HP[ahead][ahead] + HP[ahead][tied] + HP[ahead][behind]
    print("Handstrength (current board):")
    print("Ahead weighted sum: ", HPTotal[ahead])
    print("Behind weighted sum: ", HPTotal[behind])
    print("Tied weighted sum: ", HPTotal[tied])
    hs = (HPTotal[ahead]+HPTotal[tied]/2) / (HPTotal[ahead]+HPTotal[behind]+HPTotal[tied])
    print("Handstrength one opponent: ", hs)
            
    print("TRANSITIONS (currently ahead)")
    print("Total simulations sarting ahead: ", sumAhead)
    print("Ahead-Ahead: ", HP[ahead][ahead])
    print("Ahead-Tied: ", HP[ahead][tied])
    print("Ahead-Behind: ", HP[ahead][behind])
            
    print("TRANSITIONS (currently behind)")
    print("Total simulations sarting behind: ", sumBehind)
    print("Behind-Ahead: ", HP[behind][ahead])
    print("Behind-Tied: ", HP[behind][tied])
    print("Behind-Behind", HP[behind][behind])
        
    print("TRANSITIONS (currently tied)")
    print("Total simulations sarting tied: ", sumTied)
    print("Tied-Ahead: ", HP[tied][ahead])
    print("Tied-Tied: ", HP[tied][tied])
    print("Tied-Behind: ", HP[tied][behind])

class Group02Player(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

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

    def get_fitness(self):
        return self.fitness

    def mutate(self):
        """
        Mutate and change form!
        """
        self.weights = normalize(self.weights * (1 + np.random.uniform(-0.2, 0.2, size=3)))

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        if isActionTimed:      
            start = time.time()

        uuid = 0
        for p in round_state['seats']:
            if (p['name'] == 'Group02Player'):
                uuid = p['uuid']

        cards = list(map(lambda x: Card.from_str(x), hole_card))
        player = round_state['next_player']
        game_state = get_game_state(round_state, cards, uuid)
        game = Game(cards,player,game_state, NUM_ROUNDS, valid_actions,round_state, self.weights)
        
        if isDebug:
            print("Getting action...")
        
        action = game.minimax(game_state, MINIMAX_DEPTH)
        
        if isDebug:
            print("================Action selected...")

        if isActionTimed:
            end = time.time()
            print("..............Action selected in TIME: " + str(end - start) + " secs")

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
        if isDebug:        
            print("Evaluating heuristics")
        if isHeuristicTimed:        
            start = time.time()
            print(time.time())

        win_rate = estimate_hole_card_win_rate(self.num_rounds, 2, self.hole_card, state['table']._community_card)
        # print("1. Win rate done")        
        amount_in_pot = self.round_state['pot']['main']['amount']
        # print("2. Amount in pot done")        
        EHS = EffectiveHandStrength(self.hole_card, state['table']._community_card)
        # print("3. Hand strength done")
        # time.sleep(0.2)
        # if isDebug:
            # print("=======Got heuristics") 
        if isHeuristicTimed:
            end = start = time.time()
            print("==========Got heuristics in time: " + str(end-start) + " secs")

        heuristics = [win_rate, amount_in_pot, EHS]
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
            if isDebug:
                print("In MIN")
        
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
            if isDebug:
                print("In MAX")
        
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


# https://github.com/worldveil/deuces
# e.g. hole_cards = ['SA', 'C2'], community_cards = ['D9', 'H3', 'C5', 'S6', 'D4']
from deuces import Card
from deuces import Evaluator
evaluator = Evaluator()

all_cards = []
all_cards.append(Card.new('Ad'))
for i in xrange(8):
    all_cards.append(Card.new(str(i+2)+'d'))
all_cards.append(Card.new('Td'))
all_cards.append(Card.new('Jd'))
all_cards.append(Card.new('Qd'))
all_cards.append(Card.new('Kd'))

all_cards.append(Card.new('Ac'))
for i in xrange(8):
    all_cards.append(Card.new(str(i+2)+'c'))
all_cards.append(Card.new('Tc'))
all_cards.append(Card.new('Jc'))
all_cards.append(Card.new('Qc'))
all_cards.append(Card.new('Kc'))

all_cards.append(Card.new('Ah'))
for i in xrange(8):
    all_cards.append(Card.new(str(i+2)+'h'))
all_cards.append(Card.new('Th'))
all_cards.append(Card.new('Jh'))
all_cards.append(Card.new('Qh'))
all_cards.append(Card.new('Kh'))

all_cards.append(Card.new('As'))
for i in xrange(8):
    all_cards.append(Card.new(str(i+2)+'s'))
all_cards.append(Card.new('Ts'))
all_cards.append(Card.new('Js'))
all_cards.append(Card.new('Qs'))
all_cards.append(Card.new('Ks'))


def eval_post_flop_rank(hole_cards, community_cards):
    board = []
    hand = []
    for card in hole_cards:
        hand.append(Card.new(card[1]+card[0].lower()))  # 9c, Ah, Kd etc..
    for card in community_cards:
        board.append(Card.new(card[1]+card[0].lower()))

    score = evaluator.evaluate(board, hand)
    return (7462 - score + 1)/7462.0*100  # there are only 7642 distinctly ranked hands in poker


def eval_post_flop_current(hole_cards, community_cards):
    board = []
    hand = []
    remaining_cards = all_cards[:]
    for card in hole_cards:
        new_card = Card.new(card[1]+card[0].lower())
        hand.append(new_card)
        remaining_cards.remove(new_card)
    for card in community_cards:
        new_card = Card.new(card[1]+card[0].lower())
        board.append(new_card)
        remaining_cards.remove(new_card)

    score = evaluator.evaluate(board, hand)

    rounds = 0
    wins = 0
    draws = 0
    for i in xrange(0, len(remaining_cards)):
        for j in xrange(i+1, len(remaining_cards)):
            rounds += 1
            opp_hand = [remaining_cards[i], remaining_cards[j]]
            opp_score = evaluator.evaluate(board, opp_hand)
            if(opp_score > score):
                wins += 1
            # elif(evaluator.evaluate(board, opp_hand) < score):
            #     loses += 1
            elif(opp_score == score):
                draws += 1
    print("Rounds played: " + str(rounds) + " Wins: " + str(wins) + " Draws: " + str(draws))
    return 100.0 * (float(wins)/rounds)


def eval_post_flop_true(hole_cards, community_cards):
    board = []
    hand = []
    remaining_cards = all_cards[:]
    for card in hole_cards:
        new_card = Card.new(card[1]+card[0].lower())
        hand.append(new_card)
        remaining_cards.remove(new_card)
    for card in community_cards:
        new_card = Card.new(card[1]+card[0].lower())
        board.append(new_card)
        remaining_cards.remove(new_card)

    rounds = 0
    wins = 0
    draws = 0

    if(len(community_cards) == 5):  # (45 choose 2) = 990 iterations
        score = evaluator.evaluate(board, hand)
        for i in xrange(0, len(remaining_cards)):
            for j in xrange(i+1, len(remaining_cards)):
                rounds += 1
                opp_hand = [remaining_cards[i], remaining_cards[j]]
                opp_score = evaluator.evaluate(board, opp_hand)
                if(opp_score > score):
                    wins += 1
                # elif(evaluator.evaluate(board, opp_hand) < score):
                #     loses += 1
                elif(opp_score == score):
                    draws += 1
        print("Rounds played: " + str(rounds) + " Wins: " + str(wins) + " Draws: " + str(draws))
        return (float(wins)/rounds) * 100.0
    elif(len(community_cards) == 4):  # (46 choose 3) * (3 choose 1) = 45540 iterations
        for i in range(0, len(remaining_cards)):
            temp_board = board + [remaining_cards[i]]
            for j in xrange(0, len(remaining_cards)):
                if(i == j):
                    continue
                else:
                    for k in xrange(j+1, len(remaining_cards)):
                        if((i == k) or (j == k)):
                            continue
                        else:
                            rounds += 1
                            opp_hand = [remaining_cards[j], remaining_cards[k]]
                            opp_score = evaluator.evaluate(temp_board, opp_hand)
                            score = evaluator.evaluate(temp_board, hand)
                            if(opp_score > score):
                                wins += 1
                            # elif(evaluator.evaluate(board, opp_hand) < score):
                            #     loses += 1
                            elif(opp_score < score):
                                draws += 1
        print("Rounds played: " + str(rounds) + " Wins: " + str(wins) + " Draws: " + str(draws))
        return (float(wins)/rounds) * 100.0
    elif(len(community_cards) == 3):  # (47 choose 4) * (4 choose 2) = 1070190 iterations
        for h in xrange(0, len(remaining_cards)):
            temp_board = board + [remaining_cards[h]]
            for i in xrange(h+1, len(remaining_cards)):
                temp_board_2 = temp_board + [remaining_cards[i]]
                for j in xrange(0, len(remaining_cards)):
                    if((i == j) or (h == j)):
                        continue
                    else:
                        for k in xrange(j+1, len(remaining_cards)):
                            if((i == k) or (h == k)):
                                continue
                            else:
                                rounds += 1
                                # print(rounds)
                                opp_hand = [remaining_cards[j], remaining_cards[k]]
                                opp_score = evaluator.evaluate(temp_board_2, opp_hand)
                                score = evaluator.evaluate(temp_board_2, hand)
                                if(opp_score > score):
                                    wins += 1
                                # elif(evaluator.evaluate(board, opp_hand) < score):
                                #     loses += 1
                                elif(opp_score < score):
                                    draws += 1
        print("Rounds played: " + str(rounds) + " Wins: " + str(wins) + " Draws: " + str(draws))
        return (float(wins)/rounds) * 100.0
    else:
        print("ERROR")


# def eval_post_flop_hashed(hole_cards, community_cards):
#     # Sort cards by largest rank then largest suit
#     # A > K > Q > J > 10
#     # S > H > C > D
#     # DT > S9
#     # 0=SA, 1=HA, 2=CA, 3=DA, 4=SK...
#     # int('11111111', 2) convert binary to integer
#
#     suit_augment = {'S':0, 'H':1, 'C':2, 'D':3}
#
#     parsed_hole_cards = []
#     parsed_community_cards = []
#
#     for card in hole_cards:
#         if(card[1].isdigit()):
#             parsed_hole_cards.append((int(card[1] - 9) * 4 + 20) + suit_augment[card[0]])
#         elif(card[1] == 'A'):
#             parsed_hole_cards.append(0 + suit_augment[card[0]])
#         elif(card[1] == 'K'):
#             parsed_hole_cards.append(4 + suit_augment[card[0]])
#         elif(card[1] == 'Q'):
#             parsed_hole_cards.append(8 + suit_augment[card[0]])
#         elif(card[1] == 'K'):
#             parsed_hole_cards.append(12 + suit_augment[card[0]])
#         elif(card[1] == 'T'):
#             parsed_hole_cards.append(16 + suit_augment[card[0]])
#     parsed_hole_cards.sort()
#
#     for card in community_cards:
#         if(card[1].isdigit()):
#             parsed_community_cards.append((int(card[1] - 9) * 4 + 20) + suit_augment[card[0]])
#         elif(card[1] == 'A'):
#             parsed_community_cards.append(0 + suit_augment[card[0]])
#         elif(card[1] == 'K'):
#             parsed_community_cards.append(4 + suit_augment[card[0]])
#         elif(card[1] == 'Q'):
#             parsed_community_cards.append(8 + suit_augment[card[0]])
#         elif(card[1] == 'K'):
#             parsed_community_cards.append(12 + suit_augment[card[0]])
#         elif(card[1] == 'T'):
#             parsed_community_cards.append(16 + suit_augment[card[0]])
#     parsed_community_cards.sort()
#
#     parsed_cards = parsed_hole_cards + parsed_community_cards
#
#     hash = parsed_cards[0] * 0000  # 25989600/51=509600  51 because can't be 52, the smallest card
#     hash = hash + (parsed_cards[1] - 1) * 0000  # 51+50+49...+1=51*52/2=1326 can't be bigger than parsed_cards[0]
#     if(parsed_cards[2] > parsed_cards[1]):  # 2 card numbers skipped
#         hash = hash + (parsed_cards[2] - 2) * 0000  # 48 because can't be the smallest 2 remaining cards
#         hash = hash + (parsed_cards[3] - 3) * 1176  # 48+47+...+1=1176
#         hash = hash + (parsed_cards[4] - 4) * 1128  # 47+46+...+1=1128
#     elif(parsed_cards[2] < parsed_cards[0]):
#         hash = hash + (parsed_cards[2]) * 1234
#     else:
#         hash = hash + (parsed_cards[2] - 1) * 1234  # 1 card number skipped as it is in between the two hole cards
#
#     if(parsed_cards[4]>parsed_cards[1])
#
#     52C5
#     52!/((52-5)!5!)
#     52*51*...1/((47*46*...)*(5*4*3*2*1))
#     52*51*50*49*48/(5*4*3*2)
#
#     5C2
#     5*4*3*2*1/(3*2*1*2*1)
#     5*4/2
#
#     52C5*5C2
#     52*51*50*49*48/(5*4*3*2)*5*4/2
#     52*51*50*49*48/(3*4)
#     52*51*50*49*48/12
#
# [0, 1, 2, 3, 4] => #1
# [0, 1, 2, 3, 5] => #2
# [0, 1, 2, 3, 51] => #47
# [0, 1, 2, 4, 5] => #48
# [2, 3, 0, 1, 2] => #?
# [47, 48, 49, 50, 51] = > #25989600  25989600-51*50*49*48*47=-255897600
#
# (0-0)*(1-1)*(2-2)*(3-3)*(4-4) + 1
#
#     # [SA,HA] [CA,DA,SK] = 1
#     # [0, 1] [2, 3, 4] = 1
#     # 1326 combi, 19600 combi
#     # 1/1326, 1/19600 = 1
#     # 52 * 51
#
#     if(len(community_cards) == 4):
#         pass
#     elif(if(len(community_cards) == 3)):
#         pass


if __name__ == "__main__":
    import time
    # from deuces import Deck
    # deck = Deck()
    # community_cards = deck.draw(5)
    # hole_cards = deck.draw(2)
    print("\n--Five community cards test--")
    hole_cards = ['CA', 'C2']
    print(hole_cards)
    # Card.print_pretty_cards(community_cards)
    community_cards = ['D9', 'H3', 'C5', 'S6', 'D4']
    print(community_cards)
    # Card.print_pretty_cards(hole_cards)
    print("----------------------------")
    print("Algo based purely on current hand strength against all possible hands")
    start = time.time()
    print("Winrate: " + str(eval_post_flop_rank(hole_cards, community_cards)))
    print("Time taken: " + str((time.time() - start)*1000) + "ms\n")
    print("Algo calculates winrate on current hole and community cards against possible opponent hole cards")
    start = time.time()
    print("Winrate: " + str(eval_post_flop_current(hole_cards, community_cards)))
    print("Time taken: " + str((time.time() - start)*1000) + "ms\n")
    print("Algo calculates true winrate")
    start = time.time()
    print("Winrate: " + str(eval_post_flop_true(hole_cards, community_cards)))
    print("Time taken : " + str((time.time() - start)*1000) + "ms\n")

    # deck = Deck()
    # community_cards = deck.draw(4)
    # hole_cards = deck.draw(2)
    print("\n--Four community cards test--")
    hole_cards = ['CA', 'C2']
    print(hole_cards)
    # Card.print_pretty_cards(hole_cards)
    community_cards = ['D9', 'H3', 'C5', 'S6']
    print(community_cards)
    # Card.print_pretty_cards(community_cards)
    print("----------------------------")
    print("Algo based purely on current hand strength against all possible hands")
    start = time.time()
    print("Winrate: " + str(eval_post_flop_rank(hole_cards, community_cards)))
    print("Time taken: " + str((time.time() - start)*1000) + "ms\n")
    print("Algo calculates winrate on current hole and community cards against possible opponent hole cards")
    start = time.time()
    print("Winrate: " + str(eval_post_flop_current(hole_cards, community_cards)))
    print("Time taken: " + str((time.time() - start)*1000) + "ms\n")
    print("Algo calculates true winrate")
    start = time.time()
    print("Winrate: " + str(eval_post_flop_true(hole_cards, community_cards)))
    print("Time taken : " + str((time.time() - start)*1000) + "ms\n")

    # deck = Deck()
    # community_cards = deck.draw(3)
    # hole_cards = deck.draw(2)
    print("\n--Three community cards test--")
    hole_cards = ['CA', 'C2']
    print(hole_cards)
    # Card.print_pretty_cards(hole_cards)
    community_cards = ['D9', 'H3', 'C5']
    print(community_cards)
    # Card.print_pretty_cards(community_cards)
    print("----------------------------")
    print("Algo based purely on current hand strength against all possible hands")
    start = time.time()
    print("Winrate: " + str(eval_post_flop_rank(hole_cards, community_cards)))
    print("Time taken: " + str((time.time() - start)*1000) + "ms\n")
    print("Algo calculates winrate on current hole and community cards against possible opponent hole cards")
    start = time.time()
    print("Winrate: " + str(eval_post_flop_current(hole_cards, community_cards)))
    print("Time taken: " + str((time.time() - start)*1000) + "ms\n")
    print("Algo calculates true winrate")
    start = time.time()
    print("Winrate: " + str(eval_post_flop_true(hole_cards, community_cards)))
    print("Time taken : " + str((time.time() - start)*1000) + "ms\n")

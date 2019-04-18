# Format:
#    | A  | K  | Q  | J  | T  | 9  | 8  | 7  | 6  | 5  | 4  | 3  | 2  |
# A: | 85 | 67 | 67 | 66 | 65 | 64 | 63 | 63 | 62 | 61 | 60 | 59 | 58 |
# K: | 66 | 83 | 64 | 64 | 63 | 61 | 59 | 59 | 58 | 58 | 56 | 56 | 55 |
# Q: | 65 | 62 | 80 | 61 | 61 | 59 | 57 | 56 | 55 | 54 | 54 | 53 | 52 |
# J: | 65 | 61 | 59 | 78 | 59 | 57 | 56 | 54 | 53 | 52 | 52 | 50 | 49 |
# T: | 63 | 61 | 58 | 58 | 75 | 56 | 54 | 53 | 51 | 49 | 49 | 48 | 46 |
# 9: | 62 | 59 | 57 | 55 | 53 | 73 | 53 | 51 | 49 | 47 | 46 | 45 | 45 |
# 8: | 61 | 57 | 55 | 53 | 51 | 50 | 70 | 50 | 48 | 47 | 44 | 43 | 42 |
# 7: | 61 | 57 | 53 | 52 | 50 | 48 | 48 | 67 | 48 | 46 | 44 | 42 | 40 |
# 6: | 59 | 56 | 53 | 49 | 48 | 47 | 45 | 45 | 64 | 46 | 44 | 43 | 40 |
# 5: | 59 | 56 | 52 | 49 | 46 | 45 | 43 | 43 | 43 | 60 | 43 | 40 | 39 |
# 4: | 57 | 54 | 51 | 48 | 46 | 43 | 42 | 41 | 41 | 40 | 58 | 40 | 38 |
# 3: | 57 | 53 | 50 | 47 | 45 | 42 | 39 | 39 | 39 | 38 | 36 | 54 | 37 |
# 2: | 56 | 52 | 49 | 47 | 44 | 41 | 39 | 37 | 37 | 35 | 34 | 33 | 51 |

table = {'14':[], '13':[], '12':[], '11':[], '10':[], '9':[], '8':[], '7':[], '6':[], '5':[], '4':[], '3':[], '2':[]}
table['14'] = [84.97, 65.28, 64.41, 63.55, 62.66, 60.68, 59.72, 58.61, 57.26, 57.31, 56.38, 55.60, 54.84]
table['13'] = [63.49, 82.10, 61.58, 60.69, 59.82, 57.89, 56.08, 55.13, 53.98, 53.15, 52.20, 51.39, 50.58]
table['12'] = [62.57, 59.58, 79.63, 58.43, 57.56, 55.62, 53.85, 51.96, 51.02, 50.18, 49.23, 48.41, 47.56]
table['11'] = [61.63, 58.64, 56.25, 77.16, 55.67, 53.65, 51.87, 50.01, 48.03, 47.41, 46.45, 45.62, 44.79]
table['10'] = [60.70, 57.72, 55.31, 53.34, 74.66, 52.05, 50.21, 48.35, 46.39, 44.65, 43.91, 43.08, 42.24]
table['9'] = [58.60, 55.64, 53.25, 51.16, 49.47, 71.69, 48.63, 46.78, 44.85, 43.14, 41.22, 40.61, 39.78]
table['8'] = [57.54, 53.68, 51.34, 49.25, 47.49, 45.85, 68.72, 45.57, 43.58, 41.87, 39.98, 38.16, 37.58]
table['7'] = [56.36, 52.68, 49.32, 47.28, 45.51, 43.87, 42.58, 65.72, 42.60, 40.93, 39.06, 37.25, 35.40]
table['6'] = [54.91, 51.44, 48.29, 45.16, 43.42, 41.78, 40.44, 39.39, 62.58, 40.16, 38.30, 36.51, 34.68]
table['5'] = [54.94, 50.54, 47.39, 44.47, 41.54, 39.94, 38.63, 37.63, 36.83, 59.65, 38.54, 36.76, 34.93]
table['4'] = [53.95, 49.51, 46.36, 43.43, 40.75, 37.89, 36.60, 35.61, 34.82, 35.08, 56.26, 35.74, 33.95]
table['3'] = [53.08, 48.61, 45.46, 42.54, 39.84, 37.23, 34.64, 33.67, 32.90, 33.16, 32.08, 52.84, 33.12]
table['2'] = [52.24, 47.73, 44.56, 41.65, 38.94, 36.34, 33.99, 31.68, 30.91, 31.21, 30.14, 29.29, 49.41]


def eval_pre_flop(hole_cards):
    """Return winrate of hole cards
    Does not include draw rate.
    Data is for 2 players.
    https://www.cs.indiana.edu/~kapadia/nofoldem/2_wins.stats
    e.g. hole_cards = ['SA', 'C2']
    """

    if(hole_cards[0][1] == hole_cards[1][1]):  # Pair
        if(hole_cards[0][1].isdigit()):
            return table[hole_cards[0][1]][14 - int(hole_cards[0][1])]
        elif(hole_cards[0][1] == 'A'):
            return table['14'][0]
        elif(hole_cards[0][1] == 'T'):
            return table['10'][4]
        elif(hole_cards[0][1] == 'J'):
            return table['11'][3]
        elif(hole_cards[0][1] == 'Q'):
            return table['12'][2]
        elif(hole_cards[0][1] == 'K'):
            return table['13'][1]

    else:
        if(hole_cards[0][1].isdigit()):
            first_card = int(hole_cards[0][1])
        elif(hole_cards[0][1] == 'A'):
            first_card = 14
        elif(hole_cards[0][1] == 'T'):
            first_card = 10
        elif(hole_cards[0][1] == 'J'):
            first_card = 11
        elif(hole_cards[0][1] == 'Q'):
            first_card = 12
        elif(hole_cards[0][1] == 'K'):
            first_card = 13

        if(hole_cards[1][1].isdigit()):
            second_card = int(hole_cards[1][1])
        elif(hole_cards[1][1] == 'A'):
            second_card = 14
        elif(hole_cards[1][1] == 'T'):
            second_card = 10
        elif(hole_cards[1][1] == 'J'):
            second_card = 11
        elif(hole_cards[1][1] == 'Q'):
            second_card = 12
        elif(hole_cards[1][1] == 'K'):
            second_card = 13

        if(hole_cards[0][0] == hole_cards[1][0]):  # Same suit
            if(first_card > second_card):
                return table[str(first_card)][14 - second_card]
            else:
                return table[str(second_card)][14 - first_card]
        else:
            if(first_card > second_card):
                return table[str(second_card)][14 - first_card]
            else:
                return table[str(first_card)][14 - second_card]


if __name__ == "__main__":
    import time
    hole_cards = ['SA', 'C2']
    print(hole_cards)
    start = time.time()
    winrate = eval_pre_flop(hole_cards)
    print("Winrate: " + str(winrate))
    print("Time taken: " + str((time.time() - start)*1000) + "ms")

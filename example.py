from pypokerengine.api.game import setup_config, start_poker
import numpy as np
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer

from Group02PlayerConfig import Group02Player

#TODO:config the config as our wish
config = setup_config(max_round=500, initial_stack=10000, small_blind_amount=20)

config.register_player(name="FT1", algorithm=RaisedPlayer())
# config.register_player(name="AI_2", algorithm=Group02Player(np.array([0.44581346, 0.30448666, 0.24969988])))
w1 = 0.499971
w2 = 0.1
w3 = 1 - w1 - w2
config.register_player(name="AI_2", algorithm=Group02Player(np.array([w1, w2, w3])))


# 0.239977, 0.364758, 0.395265

game_result = start_poker(config, verbose=0)
print(game_result)
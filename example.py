from pypokerengine.api.game import setup_config, start_poker
from randomplayer import RandomPlayer
from raise_player import RaisedPlayer
from MiniMaxPlayer import MiniMaxPlayer

#TODO:config the config as our wish
config = setup_config(max_round=1, initial_stack=10000, small_blind_amount=10)



config.register_player(name="FT1", algorithm=RaisedPlayer())
#config.register_player(name="FT2", algorithm=RandomPlayer())
#config.register_player(name="FT3", algorithm=HonestPlayer())
config.register_player(name="FT4", algorithm=MiniMaxPlayer())

game_result = start_poker(config, verbose=0)

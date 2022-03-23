
import numpy as np

import logic


class API:
    def __init__(self):
        self._turn = 0
        self._board = None
        self._players_loc = None
        self._scores = None
        self._map_size = None

    def update(self, game):
        if isinstance(game, logic.game.Game):
            self._turn = game.turn
            self._board = game.board
            self._players_loc = game.players_loc
            self._scores = game.scores
            self._map_size = game.map_size

    @property
    def turn(self):
        return self._turn

    @property
    def board(self):
        return self._board

    def get_score(self, player_id):
        return self._scores[player_id+1]

    @property
    def players_location(self):
        return self._players_loc

    @property
    def amount_players(self):
        return len(self._players_loc)

    def check_valid_move(self, player_id, move_vector):
        player_loc = self._players_loc[player_id]
        return logic.game.Game.check_valid_move(self._map_size, move_vector, player_loc)

    def check_location_equal(self, loc1, loc2):
        return np.alltrue(loc1 == loc2)

    def location_in_array(self, loc, array):
        for aloc in array:
            if self.check_location_equal(loc, aloc):
                return True
        return False

    def check_cell_color(self, bot_id, loc):
        return self.board[loc[0], loc[1]] == bot_id + 1

# This is the Base Bot, if you want to make your own call super in your init and override bot_logic
class Bot:
    say = '"say" not specified'
    name = 'missing name'

    def __init__(self, api, bot_id):
        self.__bot_id = bot_id

    @property
    def bot_id(self):
        return self.__bot_id

    def bot_logic(self, api):
        return np.zeros(2, dtype=np.int)


import numpy as np

import logic.game


class API:
    def __init__(self):
        self._turn = 0
        self._board = None
        self._players_loc = None
        self._scores = None

    def update(self, game):
        if isinstance(game, logic.game.Game):
            self._turn = game.turn
            self._board = game.board
            self._players_loc = game.players_loc
            self._scores = game.scores

    @property
    def turn(self):
        return self._turn

    @property
    def board(self):
        return self._board

    def get_score(self, player_id):
        return self._scores[player_id]

    @property
    def players_location(self):
        return self._players_loc

    @property
    def amount_players(self):
        return len(self._players_loc)

    def check_valid_move(self, player_id, move_vector):
        player_loc = self._players_loc[player_id]
        return logic.game.Game.check_valid_move(move_vector, player_loc)


# This is the Base Bot, if you want to make your own call super in your init and override bot_logic
class Bot:
    def __init__(self, api, bot_id):
        self.bot_id = bot_id
        self.score = api.get_score(bot_id)

    def bot_logic(self, api):
        self.score = api.get_score(self.bot_id)
        return np.random.randint(-1, 2, (2,), dtype=int)

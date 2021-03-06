import numpy as np
from bots.api import API, Bot

# Settings
MINIMUM_MAP_SIZE = (2, 2)
DEFAULT_MAP_SIZE = (5, 5)
DEFAULT_PLAYER_AMOUNT = 4
DEFAULT_MAX_TURNS = 100
DEFAULT_DEBUG_STATE = False


class Game:
    def __init__(self, bots=None, game_length=DEFAULT_MAX_TURNS, map_size=None, debug=DEFAULT_DEBUG_STATE, spawn_points=None):
        self.turn = 0
        self.max_turns = game_length
        self.board = None
        self.players_loc = None
        self.is_debug = debug
        self.api = API()
        self.players_bots = [Bot]*DEFAULT_PLAYER_AMOUNT if bots is None else bots
        self.map_size = DEFAULT_MAP_SIZE if map_size is None else map_size
        sp = np.array([[0, 0], [self.map_size[0]-1, self.map_size[1]-1], [0, self.map_size[1]-1], [self.map_size[0]-1, 0]], dtype=int)
        self.spawn_points = sp if spawn_points is None else spawn_points

        assert len(self.map_size) == 2 and self.map_size[0] >= MINIMUM_MAP_SIZE[0] and self.map_size[1] >= MINIMUM_MAP_SIZE[1]
        assert len(self.spawn_points) >= len(self.players_bots)
        assert 1 < len(self.players_bots) < 5

        if not all((self._board_init(self.map_size), self._players_init(), self._bot_init())):
            raise Exception("Initialization Error")

    def do_turn(self):
        if not self.is_game_over:
            self.turn += 1
            self.api.update(self)
            self.turn_handler()
        elif self.is_debug:
            print("GAME OVER")

    def game_handler(self):
        for i in range(self.max_turns):
            self.turn = i
            if self.is_debug:
                print(f"Turn:{i}")
            self.api.update(self)
            self.turn_handler()

    def turn_handler(self):
        for i, bot in enumerate(self.players_bots):
            dest = self.check_move_vector(bot.bot_logic(api=self.api), self.players_loc[i])
            if dest is None:
                continue
            self.players_loc[i] = dest

            if self.is_debug:
                print(f"Player {i} is Moving To {dest}")
                print(self.board)

        for i, pos in enumerate(self.players_loc):
            if self._multi_player_check(i, pos):
                self.board[pos[0], pos[1]] = 0
            else:
                self.board[pos[0], pos[1]] = i + 1

    def _board_init(self, map_size):
        self.board = np.zeros(shape=map_size, dtype=int)
        sp_y = self.spawn_points[:, 0]
        sp_x = self.spawn_points[:, 1]

        if len(self.spawn_points) != self.player_count:
            sp_y = sp_y[:-(len(self.spawn_points) - self.player_count)]
            sp_x = sp_x[:-(len(self.spawn_points) - self.player_count)]
        np.add.at(self.board, (sp_y, sp_x), np.arange(1, self.player_count+1, dtype=int))
        return True

    def _players_init(self):
        delta_players = -(len(self.spawn_points) - self.player_count)
        self.players_loc = (self.spawn_points[:delta_players, :] if abs(delta_players) != 0 else self.spawn_points).copy()
        self._board_player_check()
        return True

    def _bot_init(self):
        self.api.update(self)
        for i, bot in enumerate(self.players_bots):
            self.players_bots[i] = bot(self.api, i)
        return True

    def _multi_player_check(self, i, loc):
        for j, ploc in enumerate(self.players_loc):
            if j == i:
                continue
            if np.alltrue(ploc == loc):
                return True
        return False

    def _board_player_check(self):
        for i, pos in enumerate(self.players_loc):
            if self._multi_player_check(i, pos):
                self.board[pos[0], pos[1]] = 0

    def get_winner(self):
        if self.is_game_over:
            return np.argmax(self.scores) - 1
        return None

    def toggle_debug(self):
        self.is_debug = not self.is_debug

    @property
    def scores(self):
        a = Game.get_score(self.board)
        a.resize((self.player_count+1,), refcheck=False)
        return a

    @property
    def is_game_over(self):
        return self.turn >= self.max_turns

    @property
    def player_count(self):
        return len(self.players_bots)

    @staticmethod
    def get_score(board):
        return np.bincount(board.ravel())

    def check_move_vector(self, vector, player_loc):
        if self.move_validation(vector, player_loc):
            return vector + player_loc
        return None

    def move_validation(self, move_vector, player_loc):
        return Game.check_valid_move(self.map_size, move_vector, player_loc)

    @staticmethod
    def check_valid_move(map_size, move_vector, player_loc):
        if move_vector is not None and len(move_vector) == 2:
            if move_vector[0] in [0, 1, -1] and move_vector[1] in [0, 1, -1]:
                dest = move_vector + player_loc
                if dest[0] < map_size[0] and dest[1] < map_size[1]:
                    if dest[0] >= 0 and dest[1] >= 0:
                        return True
        return False

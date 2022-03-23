import numpy as np
from bots.api import Bot


ALL_DIRECTIONS = np.array([
    [-1, 0],
    [-1, -1],
    [0, -1],
    [1, 0],
    [1, 1],
    [0, 1],
    [1, 1],
], dtype=np.int)


class NinjaBot(Bot):
    name = 'Ninja'
    say = 'I\'m a simple bot, but not that simple.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = True

    def bot_logic(self, api, debug=None):
        debug = self.debug if debug is None else debug
        if debug:
            print(f'\n\n====== NinjaBot #{self.bot_id} turn {api.turn} ======\n')
            print(f'Locations:\n{api.players_location}')
        my_pos = api.players_location[self.bot_id]
        mean_pos = np.sum(api.players_location, axis=0) / api.amount_players
        if debug:
            print(f'mean_pos: {mean_pos}')
        target_vector = api.board.shape - np.round(mean_pos)
        if debug:
            print(f'target_vector: {target_vector}')
        dir = np.array(target_vector - my_pos, dtype=np.int)
        if debug:
            print(f'dir: {dir}')
        dir[dir < -1] = -1
        dir[dir > 1] = 1
        if debug:
            print(f'final_dir: {dir}')
        target_pos = my_pos + dir
        valid_square = self.check_valid_square(api.board, target_pos)
        if valid_square:
            target_color = api.check_cell_color(self.bot_id, target_pos)
        if not valid_square or target_color:
            for new_dir in ALL_DIRECTIONS:
                target_pos = my_pos + new_dir
                valid_square = self.check_valid_square(api.board, target_pos)
                if not valid_square:
                    continue
                target_color = api.check_cell_color(self.bot_id, target_pos)
                if valid_square and not target_color:
                    dir = new_dir
                    break
        return dir

    def check_valid_square(self, board, loc):
        above_bottom = (loc < 0).sum() == 0
        below_top = (loc >= board.shape).sum() == 0
        return above_bottom and below_top


CLS = NinjaBot

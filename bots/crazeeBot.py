import random

import bots.api
import numpy as np


class CrazeeSimpleBot(bots.api.Bot):
    name = 'CrazeeBot'
    say = '00101010'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.moves = self.gen_possible_moves()

    def bot_logic(self, api):
        #print(f"CrazeeBot: id {self.bot_id}, turn:{api.turn}, score:{api.get_score(self.bot_id)}, pos:{api.players_location[self.bot_id]}")
        my_pos = api.players_location[self.bot_id]
        #priority_move_options = []
        great_move_options = []
        move_options = []
        for i, move in enumerate(self.moves):
            dest = my_pos + move
            if api.check_valid_move(self.bot_id, move):
                #Not My Cell
                if not api.check_cell_color(self.bot_id, dest):
                    great_move_options.append(move)
                else:
                    move_options.append(move)

                    #Player On the Cell
                    enemy_id = api.find_location_in_array(dest, api.players_location)
                    if enemy_id is not None:
                        my_score = api.get_score(self.bot_id)
                        enemy_score = api.get_score(enemy_id)
                        if enemy_score == max(api._scores) and enemy_score != my_score:
                            print(f"Found A Great move {move}")
                            great_move_options.append(move)

        #print(f"Normal Moves: {move_options}, Great_Moves: {great_move_options}")
        if len(great_move_options) > 0:
            return random.choice(great_move_options)
        elif len(move_options) > 0:
            return random.choice(move_options)
        return [0, 0]

    def gen_possible_moves(self):
        return np.array([[0, 0],
                         [0, 1],
                         [1, 0],
                         [1, 1],
                         [0, -1],
                         [-1, 0],
                         [-1, -1],
                         [1, -1],
                         [-1, 1],
                         ])


CLS = CrazeeSimpleBot

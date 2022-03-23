import bots.api
import numpy as np


class CrazeeSimpleBot(bots.api.Bot):
    name = 'CrazeeBot'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.moves = self.gen_possible_moves()

    def bot_logic(self, api):
        #print(f"CrazeeBot: id {self.bot_id}, turn:{api.turn}, score:{api.get_score(self.bot_id)}, pos:{api.players_location[self.bot_id]}")
        my_pos = api.players_location[self.bot_id]
        for i, move in enumerate(self.moves):
            #print(f"{i}:{move}")
            dest = my_pos + move
            if api.location_in_array(dest, api.players_location):
                #print(f"{move} has a player")
                continue
            if api.check_valid_move(self.bot_id, move):
                if api.check_cell_color(self.bot_id, dest):
                    #print(f"{move} is my color {api.check_cell_color(self.bot_id, dest)}")
                    continue
                #print(f"Crazee: Found Valid Move {move}")
                return move
            #print("Move Is Not Allowed")
        print(f"CrazeeBot: id {self.bot_id}, pos:{api.players_location[self.bot_id]} Not Moving")
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

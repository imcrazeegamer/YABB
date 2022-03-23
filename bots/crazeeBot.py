import bots.api
import numpy as np


class CrazeeSimpleBot(bots.api.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def bot_logic(self, api):
        moves = self.gen_possible_moves()
        #print(f"CrazeeBot: id {self.bot_id}, turn:{api.turn}, score:{api.get_score(self.bot_id)}, pos:{api.players_location[self.bot_id]}")
        board = api.board
        my_pos = api.players_location[self.bot_id]
        for move in moves:

            dest = my_pos + move
            #print(f"Dest:{dest}")
            #fix this
            if api.location_in_array(dest, api.players_location):
                #print(f"{move} has a player")
                continue

            if api.check_valid_move(self.bot_id, move):
                if api.check_cell_color(self.bot_id, dest):
                    #print(f"{move} is my color {board[dest[0], dest[1]]}")
                    continue
                #print(f"Crazee: Found Valid Move {move}")
                return move
            #print("Move Is Not Allowed")
        print(f"CrazeeBot: id {self.bot_id}, pos:{api.players_location[self.bot_id]} Not Moving")
        return [0, 0]

    def gen_possible_moves(self):
        arr = np.array(np.meshgrid([0, 0], [1, 1], [-1, -1])).T.reshape(-1, 2)
        return np.append(arr, np.array([[-1, -1], [1, 1]]), axis=0)



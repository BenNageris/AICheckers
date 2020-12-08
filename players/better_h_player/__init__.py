import players.simple_player as simple_player
from checkers.consts import RED_PLAYER, BLACK_PLAYER, BOARD_ROWS
from utils import MiniMaxWithAlphaBetaPruning, INFINITY, run_with_limited_time, ExceededTimeError
import abstract
from checkers.consts import EM, PAWN_COLOR, KING_COLOR, OPPONENT_COLOR, MAX_TURNS_NO_JUMP
from collections import defaultdict


class Player(simple_player.Player):
    def utility(self, state):
        if len(state.get_possible_moves()) == 0:
            return INFINITY if state.curr_player != self.color else -INFINITY
        if state.turns_since_last_jump >= MAX_TURNS_NO_JUMP:
            return 0

        piece_counts = defaultdict(lambda: [])
        for idx, (key, value) in enumerate(state.board.items()):
            if value != EM:
                if value in piece_counts.keys():
                    piece_counts[value] += [key]
                else:
                    piece_counts[value] = [key]

        opponent_color = OPPONENT_COLOR[self.color]
        num_pieces = 0
        my_u = 0
        op_u = 0

        for pawn_location in piece_counts[PAWN_COLOR[self.color]]:
            i, j = pawn_location
            if self.color == RED_PLAYER:
                my_u = my_u + (j + 5)
            else:
                my_u = my_u + ((BOARD_ROWS - j) + 5)
            num_pieces = num_pieces + 1
        for pawn_location in piece_counts[KING_COLOR[self.color]]:
            if self.color == RED_PLAYER:
                my_u = my_u + 13
            else:
                my_u = my_u + 13
            num_pieces = num_pieces + 1
        for pawn_location in piece_counts[PAWN_COLOR[opponent_color]]:
            i, j = pawn_location
            if self.color == RED_PLAYER:
                op_u = op_u + (j + 5)
            else:
                op_u = op_u + ((BOARD_ROWS - j) + 5)
            num_pieces = num_pieces + 1
        for pawn_location in piece_counts[KING_COLOR[opponent_color]]:
            if self.color == RED_PLAYER:
                op_u = op_u + 13
            else:
                op_u = op_u + 13
            num_pieces = num_pieces + 1
        if my_u == 0:
            # I have no tools left
            return -INFINITY
        elif op_u == 0:
            # The opponent has no tools left
            return INFINITY
        else:
            return (my_u - op_u) / float(num_pieces)

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'better_h_player')

import players.simple_player as simple_player
from checkers.consts import RED_PLAYER, BLACK_PLAYER, BOARD_ROWS, BOARD_COLS
from utils import MiniMaxWithAlphaBetaPruning, INFINITY, run_with_limited_time, ExceededTimeError
import abstract
from checkers.consts import EM, PAWN_COLOR, KING_COLOR, OPPONENT_COLOR, MAX_TURNS_NO_JUMP
from collections import defaultdict


class Player(simple_player.Player):
    def utility(self, state):
        def get_piece_count(state):
            piece_counts = defaultdict(lambda: [])
            for idx, (key, value) in enumerate(state.board.items()):
                if value != EM:
                    if value in piece_counts.keys():
                        piece_counts[value] += [key]
                    else:
                        piece_counts[value] = [key]
            return piece_counts

        def simple_evaluate(piece_counts):
            """
            The function calculates and returns the strength difference between my tools - opponent tools
            :param piece_counts: dictionary of tools sorted by type
            :return: int
            """
            opponent_color = OPPONENT_COLOR[self.color]
            my_u = len(piece_counts[PAWN_COLOR[self.color]]) * 100 + len(piece_counts[KING_COLOR[self.color]]) * 175
            op_u = len(piece_counts[PAWN_COLOR[opponent_color]]) * 100 + len(
                piece_counts[KING_COLOR[opponent_color]]) * 175
            return my_u, op_u

        def evaluate_pawn_position(piece_counts):
            """
            The function returns the pawns going forward to reach goal (takes in calculation pawns position in board)
            :param piece_counts: dictionary of tools sorted by type
            :return: int
            """
            my_u = 0
            op_u = 0
            opponent_color = OPPONENT_COLOR[self.color]
            for piece_position in piece_counts[PAWN_COLOR[self.color]]:
                i, j = piece_position
                if self.color == RED_PLAYER:
                    # moving down
                    my_u = my_u + (i * i)
                else:
                    my_u = my_u + ((BOARD_ROWS - i - 1) * (BOARD_ROWS - i - 1))
            for piece_position in piece_counts[PAWN_COLOR[opponent_color]]:
                i, j = piece_position
                if opponent_color == RED_PLAYER:
                    # moving down
                    op_u = op_u + (i * i)
                else:
                    op_u = op_u + ((BOARD_ROWS - i - 1) * (BOARD_ROWS - i - 1))
            return my_u, op_u

        def corner_king(piece_counts):
            """
            The function deducts points for having king in corner - decreases its move posibility and cause traps
            :param piece_counts: dictionary of tools sorted by type
            :return: int
            """
            my_u, op_u = 0, 0
            opponent_color = OPPONENT_COLOR[self.color]
            for piece_position in piece_counts[KING_COLOR[self.color]]:
                i, j = piece_position
                if j in (0, BOARD_COLS - 1):
                    # king in the first or last column
                    my_u = my_u - 25
            for piece_position in piece_counts[KING_COLOR[opponent_color]]:
                i, j = piece_position
                if j in (0, BOARD_COLS - 1):
                    # king in the first or last column
                    op_u = op_u - 25
            return my_u, op_u

        if len(state.get_possible_moves()) == 0:
            return INFINITY if state.curr_player != self.color else -INFINITY
        if state.turns_since_last_jump >= MAX_TURNS_NO_JUMP:
            return 0

        piece_counts = get_piece_count(state)

        # when pawn are also left -- need to think about strategy for only kings in game
        simple_evaluate_my, simple_evaluate_op = simple_evaluate(piece_counts)
        position_evaluate_my, position_evaluate_op = evaluate_pawn_position(piece_counts)
        corner_evaluate_my, corner_evaluate_op = corner_king(piece_counts)
        # corner_evaluate_my, corner_evaluate_op = 0, 0
        if simple_evaluate_my == 0:
            # I have no tools left
            return -INFINITY
        elif simple_evaluate_op == 0:
            # The opponent has no tools left
            return INFINITY
        return (simple_evaluate_my - simple_evaluate_op) + (position_evaluate_my - position_evaluate_op) + (
                corner_evaluate_my - corner_evaluate_op)

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'better_h_player')

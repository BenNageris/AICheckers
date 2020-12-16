import players.simple_player as simple_player
from checkers.consts import RED_PLAYER, BLACK_PLAYER, BOARD_ROWS, BOARD_COLS
from utils import MiniMaxWithAlphaBetaPruning, INFINITY, run_with_limited_time, ExceededTimeError
import abstract
from checkers.consts import EM, PAWN_COLOR, KING_COLOR, OPPONENT_COLOR, MAX_TURNS_NO_JUMP
from collections import defaultdict


class Player(simple_player.Player):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        simple_player.Player.__init__(self, setup_time, player_color, time_per_k_turns, k)

    def get_piece_count(self, state):
        """
        The function returns dictionary of tools with key as their type
        :param state: GameState
        :return: dictionary
        """
        piece_counts = defaultdict(lambda: [])
        for key, value in state.board.items():
            if value != EM:
                piece_counts[value].append(key)
        return piece_counts

    def simple_evaluate(self, piece_counts):
        """
        The function calculates and returns the strength difference between my tools - opponent tools
        :param piece_counts: dictionary of tools sorted by type
        :return: int
        """
        opponent_color = OPPONENT_COLOR[self.color]
        my_u = len(piece_counts[PAWN_COLOR[self.color]]) * 115 + len(piece_counts[KING_COLOR[self.color]]) * 200
        op_u = len(piece_counts[PAWN_COLOR[opponent_color]]) * 115 + len(piece_counts[KING_COLOR[opponent_color]]) * 200
        return my_u, op_u

    def evaluate_pawn_position(self, piece_counts):
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
                my_u = my_u + (i * 7)
            else:
                my_u = my_u + ((BOARD_ROWS - i - 1) * 7)
        for piece_position in piece_counts[PAWN_COLOR[opponent_color]]:
            i, j = piece_position
            if opponent_color == RED_PLAYER:
                # moving down
                op_u = op_u + (i * 7)
            else:
                op_u = op_u + ((BOARD_ROWS - i - 1) * 7)
        return my_u, op_u

    def is_only_kings_remain(self, piece_counts):
        """
        The function returns whether only kings remained in the game (time for new evaluation)
        :param piece_counts: dictionary of tools sorted by type
        :return: int
        """
        opponent_color = OPPONENT_COLOR[self.color]
        return len(piece_counts[PAWN_COLOR[self.color]]) == 0 and len(piece_counts[PAWN_COLOR[opponent_color]]) == 0

    def corner_pawn(self, piece_counts):
        """
        The function deducts points for having king in corner - decreases its move posibility and cause traps
        :param piece_counts: dictionary of tools sorted by type
        :return: int
        """
        my_u, op_u = 0, 0
        opponent_color = OPPONENT_COLOR[self.color]
        for piece_position in piece_counts[PAWN_COLOR[self.color]]:
            i, j = piece_position
            if j in (0, BOARD_COLS - 1):
                if self.color == RED_PLAYER:
                    rows_passed = i
                else:
                    rows_passed = BOARD_ROWS - 1 - i
                my_u = my_u + (15 + rows_passed)
        for piece_position in piece_counts[PAWN_COLOR[opponent_color]]:
            i, j = piece_position
            if j in (0, BOARD_COLS - 1):
                if self.color == RED_PLAYER:
                    rows_passed = i
                else:
                    rows_passed = BOARD_ROWS - 1 - i
                op_u = op_u + (15 + rows_passed)
        return my_u, op_u

    def _sum_of_dist(self, piece_counts):
        def distance_calculation(x1, y1, x2, y2):
            return max(abs(x2 - x1), abs(y2 - y1))

        sum_of_dist = 0
        opponent_color = OPPONENT_COLOR[self.color]
        for player_location in piece_counts[KING_COLOR[self.color]]:
            for opponent_location in piece_counts[KING_COLOR[opponent_color]]:
                distance = distance_calculation(player_location[0], player_location[1], opponent_location[0],
                                                opponent_location[1])
                if len(piece_counts[KING_COLOR[self.color]]) >= len(piece_counts[KING_COLOR[opponent_color]]):
                    # winning
                    sum_of_dist += abs(BOARD_ROWS - 1 - distance) * 4
                else:
                    sum_of_dist += distance * 4
        return sum_of_dist

    def _king_catch_opponent(self, piece_counts):
        def distance_calculation(x1, y1, x2, y2):
            return max(abs(x2 - x1), abs(y2 - y1))

        sum_of_dist = 0
        opponent_color = OPPONENT_COLOR[self.color]
        for player_location in piece_counts[KING_COLOR[self.color]]:
            for opponent_location in piece_counts[PAWN_COLOR[opponent_color]] + piece_counts[
                KING_COLOR[opponent_color]]:
                distance = distance_calculation(player_location[0], player_location[1], opponent_location[0],
                                                opponent_location[1])
                sum_of_dist += abs(BOARD_ROWS - 1 - distance) * 4
        return sum_of_dist

    def utility(self, state):
        if len(state.get_possible_moves()) == 0:
            return INFINITY if state.curr_player != self.color else -INFINITY

        if state.turns_since_last_jump >= MAX_TURNS_NO_JUMP:
            return 0
        piece_counts = self.get_piece_count(state)
        simple_evaluate_my, simple_evaluate_op = self.simple_evaluate(piece_counts)
        if simple_evaluate_my == 0:
            # I have no tools left
            return -INFINITY
        elif simple_evaluate_op == 0:
            # The opponent has no tools left
            return INFINITY
        if self.is_only_kings_remain(piece_counts):
            return simple_evaluate_my - simple_evaluate_op + self._sum_of_dist(piece_counts)
        king_catch = self._king_catch_opponent(piece_counts)
        position_evaluate_my, position_evaluate_op = self.evaluate_pawn_position(piece_counts)
        corner_pawn_evaluate_my, corner_pawn_evaluate_op = self.corner_pawn(piece_counts)
        return (simple_evaluate_my - simple_evaluate_op) + (
                position_evaluate_my - position_evaluate_op) + king_catch + (
                       corner_pawn_evaluate_my - corner_pawn_evaluate_op)

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'better_h_player')

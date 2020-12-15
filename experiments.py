import os
import sys

import csv

import run_game
from checkers.consts import BLACK_PLAYER, RED_PLAYER

LOSE_SCORE = 0
TIE_SCORE = 0.5
WIN_SCORE = 1


def run(times, players_names, result_file_name):
    # Args for runner
    # 0: setup_time, 1: round_time, 2: k, 3: verbose, 4: Player1, 5: Player2
    args = ['2', '', '5', 'n', '', '']

    # Create each match
    dous = []
    for i in range(len(players_names) - 1):
        for j in range(i + 1, len(players_names)):
            dous.append((players_names[i], players_names[j]))  # P1 vs P2
            dous.append((players_names[j], players_names[i]))  # P2 vs P1

    # Store all results to update file on the run
    results = [['TEST START']]

    experiments_counter = 0
    # Iterate times per round
    for t in times:
        args[1] = t
        for player1, player2 in dous:
            experiments_counter += 1
            print(f'Experiment #{experiments_counter}:')
            # FIRST GAME: player 1 starts
            args[4], args[5] = player1, player2
            runner = run_game.GameRunner(*args)
            winner = runner.run()

            match_result = [player1, player2, t]

            if winner == run_game.TIE:
                match_result.extend([TIE_SCORE, TIE_SCORE])
            elif winner[0] == RED_PLAYER:
                match_result.extend([WIN_SCORE, LOSE_SCORE])
            else:
                match_result.extend([LOSE_SCORE, WIN_SCORE])
            results.append(match_result)

            print(f'current result: {match_result}')

            with open('experiments.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                for row, result in enumerate(results):
                    for col, field in enumerate(result):
                        writer.writerow([row, col, field])


if __name__ == '__main__':
    T = ['2', '10', '50']
    result_file = 'results'
    players = ['simple_player', 'better_h_player', 'improved_player', 'improved_better_h_player']
    run(T, players, result_file)

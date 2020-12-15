import csv

import run_game
from checkers.consts import RED_PLAYER

T = ['2', '10', '50']
LOSING_SCORE = 0
TIE_SCORE = 0.5
WINNING_SCORE = 1


def run(players_names):
    # args contains 5 arguments:
    # setup_time, round_time, k, verbose, player1, player2
    # player1 and player2 will insert to args while execution the experiments.
    args = ['2', '', '5', 'n', '', '']

    # Create each match
    rivals = []
    for i in range(len(players_names) - 1):
        for j in range(i + 1, len(players_names)):
            rivals.append((players_names[i], players_names[j]))
            rivals.append((players_names[j], players_names[i]))
    print(rivals)

    results = []
    experiments_counter = 0
    # Iterate T per round
    for t in T:
        args[1] = t
        for player1, player2 in rivals:
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
                match_result.extend([WINNING_SCORE, LOSING_SCORE])
            else:
                match_result.extend([LOSING_SCORE, WINNING_SCORE])
            results.append(match_result)

            print(f'current result: {match_result}')

    with open('experiments.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for match in results:
            writer.writerow(match)


if __name__ == '__main__':
    players_list = ['simple_player', 'improved_player']  # ['simple_player', 'better_h_player', 'improved_player', 'improved_better_h_player']
    run(players_list)

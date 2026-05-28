from players import Player, PredictivePlayer
from game import Game
import random
import math
import matplotlib.pyplot as plt
import numpy as np

def game_over(scoreboard, games):
    for score in scoreboard.values():
        if score == games:
            return True
    return False

def main():

    nn_player1 = PredictivePlayer(None, risk=(random.random()*2)-1, use_predictive_risk=True)
    nn_player2 = PredictivePlayer(None, risk=(random.random()*2)-1, use_predictive_risk=True)
    nn_player3 = PredictivePlayer(None, risk=(random.random()*2)-1, use_predictive_risk=True)
    nn_player4 = PredictivePlayer(None, risk=(random.random()*2)-1, use_predictive_risk=True)
    nn_player5 = PredictivePlayer(None, risk=(random.random()*2)-1, use_predictive_risk=True)
    nn_player6 = PredictivePlayer(None, risk=(random.random()*2)-1, use_predictive_risk=True)

    players = [nn_player1, nn_player2, nn_player3, nn_player4, nn_player5, nn_player6]
    game = Game(players)

    games = 1000

    scoreboard = {
        nn_player1.GetName(): 0,
        nn_player2.GetName(): 0,
        nn_player3.GetName(): 0,
        nn_player4.GetName(): 0,
        nn_player5.GetName(): 0,
        nn_player6.GetName(): 0
    }

    scores = []

    batch = 0
    batches = 0
    total_games = 0
    overall_stats = {
        "hands": [],
        "rounds": []
    }

    batch_scoreboard = {
        nn_player1.GetName(): 0,
        nn_player2.GetName(): 0,
        nn_player3.GetName(): 0,
        nn_player4.GetName(): 0,
        nn_player5.GetName(): 0,
        nn_player6.GetName(): 0
    }

    player_risks = {
        nn_player1.GetName(): [],
        nn_player2.GetName(): [],
        nn_player3.GetName(): [],
        nn_player4.GetName(): [],
        nn_player5.GetName(): [],
        nn_player6.GetName(): []
    }

    player_batch_points = {
        nn_player1.GetName(): [],
        nn_player2.GetName(): [],
        nn_player3.GetName(): [],
        nn_player4.GetName(): [],
        nn_player5.GetName(): [],
        nn_player6.GetName(): []
    }

    player_points = {
        nn_player1.GetName(): [],
        nn_player2.GetName(): [],
        nn_player3.GetName(): [],
        nn_player4.GetName(): [],
        nn_player5.GetName(): [],
        nn_player6.GetName(): []
    }

    while not game_over(scoreboard, games):
        _, stats = game.PlayGame()
        game_scores = game.GetScoreboard()

        overall_stats["hands"] += stats["hands"]
        overall_stats["rounds"].append(stats["rounds"])

        # Mark wins for all victors (ties can happen)
        max_score = game_scores[0].GetGameScore()
        for player in game_scores:
            if player.GetGameScore() == max_score:
                batch_scoreboard[player.GetName()] += 1
                scoreboard[player.GetName()] += 1
            else:
                # List is sorted so can break out once first player doesn't match
                break

        game.NewGame()

        if any(score == games-1 for score in scoreboard.values()):
            game.SetNarrate(True)

        total_games += 1
        batch += 1

        if batch % 50 == 0 and not game_over(scoreboard, games):
            batches += 1
            leader = game.GetPlayerFromName(max(batch_scoreboard, key=batch_scoreboard.get))

            print(f"--- Batch {batches} complete ---\nCurrent leader is: {leader.GetName()} with risk of: {leader.GetRisk()}")
            print(scoreboard)
            print(batch_scoreboard)

            
            leader_risk = leader.GetRisk()

            for player in players:

                # Update batch records
                player_risks[player.GetName()].append(player.GetRisk())
                player_batch_points[player.GetName()].append(batch_scoreboard[player.GetName()])
                player_points[player.GetName()].append(scoreboard[player.GetName()])

                if (not player == leader):

                    if not (batch_scoreboard[leader.GetName()]/(len(players)-1) >= batch_scoreboard[player.GetName()] and batch_scoreboard[player.GetName()] == min(batch_scoreboard.values())): #and batch_scoreboard[player.GetName()] == min(scoreboard.values())):
                        # Track difference in points between player and leader, as a percentage of total games they've won combined
                        combined_games = scoreboard[leader.GetName()] + scoreboard[player.GetName()]
                        percent_point_diff = abs((scoreboard[leader.GetName()] - scoreboard[player.GetName()])/(combined_games))

                        new_risk = player.GetRisk() + ((leader_risk - player.GetRisk()) * percent_point_diff)

                        print(f"\t{player.GetName()} you will be upgraded with a new risk of: {new_risk}\n\t\t{player.GetRisk()} + ({leader_risk} - {player.GetRisk()}) * ({percent_point_diff})")
                        player.SetRisk(new_risk)
                    else:
                        combined_games = scoreboard[leader.GetName()] + scoreboard[player.GetName()]
                        win_ratio = (scoreboard[player.GetName()]+scoreboard[leader.GetName()])/total_games
                        random_float = random.gauss(leader.GetRisk(), win_ratio)
                        print(f"\t{player.GetName()} you are the weakest of the batch and scoreboard, stir chaos with a new risk of: {random_float})\n")
                        player.SetRisk(random_float)

            batch_scoreboard = {
                nn_player1.GetName(): 0,
                nn_player2.GetName(): 0,
                nn_player3.GetName(): 0,
                nn_player4.GetName(): 0,
                nn_player5.GetName(): 0,
                nn_player6.GetName(): 0
            }
            

    print(scoreboard)
    for player in players:
        print(f'{player.GetName()}: {player.GetRisk()}')

    print(f"--- Overall Report ---\nBatches:\t{batches}\nNumber hands:\t{len(overall_stats["hands"])}\nLargest hand:\t{max(overall_stats["hands"])}\nAverage hand:\t{sum(overall_stats["hands"])/len(overall_stats["hands"])}\nMedian hand:\t{overall_stats["hands"][math.floor(len(overall_stats["hands"])/2)]}\nTotal rounds:\t{sum(overall_stats["rounds"])}\nAverage rounds/game:\t{sum(overall_stats["rounds"])/total_games}")

    fig, ax = plt.subplots(3)

    for player in players:
        ax[0].plot(np.asarray(player_batch_points[player.GetName()]), label=player.GetName())

    ax[0].set_xlabel("Batch")
    ax[0].set_ylabel("Points in batch")
    ax[0].legend()
    ax[0].set_title("Player points per batch")

    for player in players:
        ax[1].plot(np.asarray(player_risks[player.GetName()]), label=player.GetName())

    ax[1].set_xlabel("Batch")
    ax[1].set_ylabel("Risk")
    ax[1].legend()
    ax[1].set_title("Player risks per batch")

    for player in players:
        ax[2].plot(np.asarray(player_points[player.GetName()]), label=player.GetName())

    ax[2].set_xlabel("Batch")
    ax[2].set_ylabel("Total points")
    ax[2].legend()
    ax[2].set_title("Player point totals over time")

    plt.show()
    
if __name__=="__main__":
    main()
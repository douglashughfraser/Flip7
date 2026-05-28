from game import Game, Player
import random
import csv
import os

def SortPlays(plays):
    return sorted(plays, key=lambda player: player["Result"], reverse=True)

def SavePlaysCSV(plays, filename="plays.csv"):
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=plays[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(plays)

def main():
    num_games = 5000

    for i in range(num_games):
        players = []
        for player in range(random.randint(3, 14)):
            players.append(Player())

        game = Game(p=players, narrate=False)
        plays = game.PlayGame()
        SavePlaysCSV(plays)   # Write and discard
        del plays             # Explicit cleanup
        print(f"Finished game {i}.")

    print(f"Done. Data saved to plays.csv")

if __name__=="__main__":
    main()
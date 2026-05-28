import random
from modelling import train_linear_regression_model, train_binary_classification_model
import pandas as pd
import torch
import torch.nn as nn

EMPTYHAND = {   
    "#12": 0,
    "#11": 0,
    "#10": 0,
    "#9":  0,
    "#8":  0,
    "#7":  0,
    "#6":  0,
    "#5":  0,
    "#4":  0,
    "#3":  0,
    "#2":  0,
    "#1":  0,
    "#0":  0,
    "SC":  0,
    "Fr":  0,
    "F3":  0,
    "+2":  0,
    "+4":  0,
    "+6":  0,
    "+8":  0,
    "+10": 0,
    "X2":  0,
}

class Player:

    _names = ["Will", "Phoebe", "Sky", "Ben", "Karina", "Kris", "Adam", "Andrew", "Ross", "Leah D", "Doug", "Becca", "Sam", "Iain", "Theo", "Leah H", "Tereza", "Zsofi"]

    def __init__(self, current_game=None, n=None):
        if n == None:
            self.name = Player._names[random.randint(0, len(Player._names)-1)]
        else:
            self.name = n

        self.hand = EMPTYHAND.copy()
        self.hand_score = 0
        self.game_score = 0
        self.bust = False
        self.passed = False
        self.frozen = False
        self.game = current_game

    # Player decides whether to ask for another card or not.
    # Returns 1 take another card, 0 to stick.

    def ChangeName(self):
        self.name = Player._names[random.randint(0, len(Player._names)-1)]

    def SetName(self, name):
        self.name = name

    def GetName(self):
        return self.name

    def RoundEnd(self):
        self.game_score += self.hand_score
        self.hand_score = 0
        self.frozen = False
        self.bust = False
        self.passed = False
        discards = self.hand.copy()
        self.hand = EMPTYHAND.copy()
        return discards

    def NewGame(self):
        self.hand = EMPTYHAND.copy()
        self.hand_score = 0
        self.game_score = 0
        self.bust = False
        self.passed = False
        self.frozen = False

    # Returns True if this player is still active. 
    # False if player has previously: bust, passed or been frozen.
    def IsActive(self):
        return not(self.bust or self.passed or self.frozen)

    def GetsFrozen(self):
        if self.frozen:
            raise Exception("I have already been frozen.")

        self.frozen = True
        self.hand["Fr"] += 1

    def HasPassed(self):
        return self.passed

    def IsBust(self):
        return self.bust

    def IsFrozen(self):
        return self.frozen

    def JoinGame(self, g):
        self.game = g

    def Flipped7(self):
        #if sum(self.hand[f"#{i}"] for i in range(13)) > 6:
        #    print(f"Flipped 7 or more: {sum(self.hand[f"#{i}"] for i in range(13))}, \n{self.hand}")
        return sum(self.hand[f"#{i}"] for i in range(13)) == 7 and self.IsActive()

    def GetHandStr(self):
        return str([card for card, count in self.hand.items() if count > 0])

    def GetGameScore(self):
        return self.game_score

    def GetHandScore(self):
        return self.hand_score

    def GetHandDict(self):
        return self.hand.copy()

    def HasSC(self):
        return self.hand["SC"] > 0

    # Player decides whether to take another card or not.
    # Returns true for another card, false to pass.
    def TakeTurn(self):
        hitme = random.randint(0,1)

        if not hitme:
            self.passed = True
        
        return hitme

    def CalculateHandScore(self):
        
        self.hand_score = sum(self.hand[f"#{i}"] * i for i in range(13))

        if self.hand["X2"] == 1: 
            self.hand_score *= 2

        self.hand_score += sum(self.hand[f"+{i}"] * i for i in range(2,12,2))

        # 15 bonus points for Flipping 7 different number cards.
        if self.Flipped7():
            self.hand_score += 15

        if self.bust:
            self.hand_score = 0

        return self.hand_score

    def ReceiveCard(self, card):

        # Check if we should be receiving a card.
        if self.bust:
            raise Exception("I am already bust.")
        elif self.passed:
            raise Exception("I have already passed.")
        elif self.frozen:
            raise Exception("I have already been frozen.")

        if card[0] == '#':
            # Add the card to the hand
            self.hand[card] += 1
            # If the player now has two copies of that card, check if they have a SC.
            if self.hand[card] > 1:
                if self.hand["SC"] == 0:
                    # If not, bust.
                    self.bust = True
                    self.hand_score = 0
                else:
                    # If they do then remove one of the duplicates and the second chance.
                    self.hand["SC"] -= 1
                    self.hand[card] -= 1

                    self.game.deck.DiscardCards[card] += 1
                    self.game.deck.DiscardCards["SC"] += 1
        elif card[0] == '+' or card == "X2":
            # Add the card to the hand.
            self.hand[card] += 1

        self.CalculateHandScore()

        # Players can choose who to play Freeze or Flip3 to, including themselves.
        if card == "Fr":
            players = self.game.GetActivePlayers()
            if players == []: 
                self.game.deck.DiscardCards["Fr"] += 1
                return None
            else:
                return players[random.randint(0, len(players)-1)]
        elif card == "F3":
            players = self.game.GetActivePlayers()
            if players == []: 
                self.game.deck.DiscardCards["F3"] += 1
                return None
            else:
                return players[random.randint(0, len(players)-1)]
        elif card == "SC":
            if self.hand["SC"] == 0:
                self.hand["SC"] += 1
            # Players can't have more than one second chance, they must give it to someone else.
            else:
                players = self.game.GetPlayersNoSC()
                # If all players have a second chance then discard it.
                if players == []:
                    self.game.deck.DiscardCards["SC"] += 1
                    return None
                else:
                    return players[random.randint(0, len(players)-1)]

        # If no choice to be made, return None.
        return None

class PredictivePlayer(Player):

    def __init__(self, current_game=None, n=None, risk=0.4, use_predictive_risk=False):

        super().__init__(current_game, n)

        # Try to load predictive model
        try:
            model_file = torch.load("./linear_regression_model_nn.pth")

            self.points_model = nn.Sequential(
                nn.Linear(model_file["input_size"], 64),
                nn.ReLU(),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 1)
            )
            self.points_model.load_state_dict(model_file["state_dict"])
            self.points_feature_columns = model_file["feature_columns"]

            self.points_model.eval()

        except FileNotFoundError:
            train_linear_regression_model()

            model_file = torch.load("./linear_regression_model_nn.pth")

            self.points_model = nn.Sequential(
                nn.Linear(model_file["input_size"], 64),
                nn.ReLU(),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 1)
            )
            self.points_model.load_state_dict(model_file["state_dict"])
            self.points_feature_columns = model_file["feature_columns"]

            self.points_model.eval()

        # Try to load predictive model
        try:
            model_file = torch.load("./binary_classification_model_nn.pth")

            self.risk_model = nn.Sequential(
                nn.Linear(model_file["input_size"], 64),
                nn.ReLU(),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 1),
                nn.Sigmoid()
            )
            self.risk_model.load_state_dict(model_file["state_dict"])
            self.risk_feature_columns = model_file["feature_columns"]

            self.risk_model.eval()

        except FileNotFoundError:
            self.risk_model = train_binary_classification_model()

            self.risk_model = nn.Sequential(
                nn.Linear(model_file["input_size"], 64),
                nn.ReLU(),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 1),
                nn.Sigmoid()
            )
            self.risk_model.load_state_dict(model_file["state_dict"])
            self.risk_feature_columns = model_file["feature_columns"]

            self.risk_model.eval()

        self.use_predictive_risk = use_predictive_risk

        # Legacy risk model
        self.risk = risk

    def GetRisk(self):
        return self.risk

    def SetRisk(self, risk):
        self.risk = risk

    def GetRiskModelType(self):
        if self.use_predictive_risk:
            return "Predictive"
        else:
            return "Parameter"

    def TakeTurn(self):
        hand = self.GetHandDict()

        hand_list = [
            hand.get(card, 0)
            for card in self.points_feature_columns
        ]

        # Make hand into a tensor
        hand_tensor = torch.tensor(hand_list, dtype=torch.float32).unsqueeze(0)

        # Get a score prediction from the model
        prediction = self.points_model(hand_tensor).item()

        if self.use_predictive_risk:
            predicted_risk = self.risk_model(hand_tensor).item()

            if float(self.GetHandScore() > prediction * ((1-predicted_risk) * self.risk)):
                hitme = False
            else:
                hitme = True

            if self.game.GetNarrate():
                print(f"\n\t{float(self.GetHandScore())} > {prediction} * {1-predicted_risk} * {self.risk})\n\t= {float(self.GetHandScore())} > {(prediction) * ((1-predicted_risk) * self.risk)})")

        # Take a new card if predicted to gain more than risk multiplier of current score.
        #print(f"{prediction}<{self.GetHandScore()*self.GetRisk()}({self.GetHandScore()}*{self.GetRisk()})\n\t{self.GetHandDict()}")
        elif not self.use_predictive_risk:
            if float(self.GetHandScore()) > prediction * (1-self.risk):
                hitme = False
            else:
                hitme = True

            if self.game.GetNarrate():
                print(f"\t{float(self.GetHandScore())} > {prediction} * {(1-self.risk)}\n\t= {float(self.GetHandScore())} > {prediction * (1-self.risk)}")


        if not hitme:
            self.passed = True
        return hitme
            
        

from deck import GameDeck
from players import Player

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

class Game:
    
    def __init__(self, p=None, d=None, narrate=False):
        if p == None:
            player1 = Player()
            player2 = Player()
            player3 = Player()
            p = [player1, player2, player3]
        if d == None:
            d = GameDeck()

        self.narrate = narrate
        self.deck = d
        self.first = 0

        # Add players to game, ensure they all have unique names.
        self.players = []
        names = []
        for player in p:
            while player.GetName() in names:
                player.ChangeName()
            names.append(player.GetName())
            self.players.append(player)
            player.JoinGame(self)

    def SetNarrate(self, narrate):
        self.narrate = narrate

    def GetNarrate(self):
        return self.narrate

    def SetDeck(self, d):
        self.deck = d

    def GetDeck(self):
        return self.deck

    def GetPlayers(self):
        return self.players

    def GetActivePlayers(self):
        active = []
        for player in self.players:
            if player.IsActive():
                active.append(player)

        return active

    def IsGameOver(self):
        return any(p.GetGameScore() >= 200 for p in self.players)
    
    def PlayersStillActive(self):
        return any(p.IsActive() == True for p in self.players)

    def GetScoreboard(self):
        return sorted(self.players, key=lambda player: player.GetGameScore(), reverse=True)

    def PrintScoreboard(self):
        print("\n--- Scoreboard ---")
        for i, player in enumerate(self.GetScoreboard(), start=1):
            print(f"{i}. {player.GetName()}: {player.GetGameScore()}")
        
    def GetPlayersNoSC(self):
        options = []
        for player in self.players:
            if not player.HasSC() and player.IsActive():
                options.append(player)
        return options

    def AddPlayers(self, additions):
        for player in additions:
            player.JoinGame(self)
            self.players.append(player)

    def GetNextActivePlayer(self, turn):
        if turn >= len(self.players):
            turn = 0
        player = self.players[turn]

        while not player.IsActive():
            turn += 1
            if turn >= len(self.players):
                turn = 0
            player = self.players[turn]

        return player

    def PlayerTurn(self, player, card = None, starting = False):
        if card == None:
            card = self.deck.DealCard()
        
        if self.narrate:
            if starting:
                print(f'{player.GetName()}\tstarts with a {card}.')
            else:    
                print(f'{player.GetName()}\twith {player.GetHandStr()}\n\tHits for a {card}!')
        chosen = player.ReceiveCard(card)

        # A non-zero response means a player has received a card.
        if chosen != None:
            if self.narrate:
                print(f'They give it to {chosen.GetName()}.')
            if card == "Fr":
                chosen.GetsFrozen()
            if card == "F3":
                self.Flip3(chosen)
            if card == "SC":
                chosen.ReceiveCard("SC")
        return chosen

    def Flip3(self, player):
        cards = []
        if self.narrate:
            print("---------------F3 START --------------------")
        for i in range(3):
            card = self.deck.DealCard()

            # If the card is an action card, bank it for later.
            if card == "Fr" or card == "F3":
                cards.append(card)
            else:
                self.PlayerTurn(player, card)

            # Stop flipping if the player busts or Flips7
            if not player.IsActive() or player.Flipped7():
                break
        for card in cards:
            if player.IsActive() and not player.Flipped7():
                self.PlayerTurn(player, card)
            else:
                # If player is no longer active, discard their remaining cards.
                self.deck.DiscardCards[card]+=1

        # Discard the Flip3.
        self.deck.CollectDiscards({"F3": 1})
        if self.narrate:
            print("---------------F3 FINISH--------------------")

    # Check all cards have been returned.
    def CheckCards(self):
        all_cards = {}
        for card in EMPTYHAND.keys():
            all_cards[card] = self.deck.DiscardCards[card] + self.deck.RemainingCards[card]

        if sum(all_cards.values()) != sum(self.deck.GetAllCards().values()):
            for player in self.players:
                print(player.GetHandDict())

            raise Exception(f'Shuffled deck: Expected {sum(self.deck.GetAllCards().values())} cards but got {sum(all_cards.values())} cards. \n{all_cards}')

    def GetPlayerFromName(self, name_str):
        for player in self.players:
            if player.GetName() == name_str:
                return player

        return None

    # Reset all player hands and scores, shuffle deck.
    def NewGame(self):
        for player in self.players:
            player.NewGame()

        self.deck.Shuffle()

    def PlayGame(self):

        plays = []
        stats = {
            "rounds": 0,
            "hands": [],
            "largest_hand": 0,
            "average_hand": 0,
        }

        if self.narrate:
            print("\n--- New Game! ---")

        self.NewGame()
        GameOn = True

        # Play another round if nobody is over 200 score.
        while not self.IsGameOver():

            self.CheckCards()

            if self.narrate:
                self.PrintScoreboard()

            for player in self.players:
                if player.IsActive():
                    self.PlayerTurn(player, starting=True)

            turn = self.first

            while len(self.GetActivePlayers()) > 0:

                player = self.GetNextActivePlayer(turn)

                if player.TakeTurn():
                    # If the player takes a card, document the hand that they had
                    play = player.GetHandDict().copy()
                    self.PlayerTurn(player)
                    if player.IsBust() & self.narrate:
                        print("\t\tBust.")
                    
                    # Add the achieved hand score to the play data.
                    play["Result"] = player.GetHandScore()
                    plays.append(play)

                elif self.narrate:
                    print(f'{player.GetName()} with {player.GetHandStr()} \n\tPasses for a score of {player.GetHandScore()}')

                turn += 1

            # Change starting player between rounds.
            if self.first == len(self.players):
                self.first = 0
            else:
                self.first += 1

            # Have players calculate their score and discard their hands.
            for player in self.players:
                stats["hands"].append(player.GetHandScore())
                discards = player.RoundEnd()
                self.deck.CollectDiscards(discards)

            stats["rounds"] += 1

        if self.narrate:
            self.PrintScoreboard()

        stats["largest_hand"] = max(stats["hands"])
        stats["average_hand"] = sum(stats["hands"])/len(stats["hands"])

        return plays, stats
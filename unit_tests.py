import unittest
from deck import GameDeck
from game import Game
from players import Player, PredictivePlayer

class TestDeck(unittest.TestCase):

    def setUp(self):
        self.Deck = GameDeck()

    def test_shuffle(self):
        pre_Shuffle = self.Deck.GetCards()
        self.Deck.Shuffle()
        post_Shuffle = self.Deck.GetCards()
        self.assertNotEqual(pre_Shuffle, post_Shuffle)

    def test_DealCard(self):
        order = self.Deck.GetCards()
        self.assertEqual(order[0], self.Deck.DealCard())

    def test_discard_collection(self):
        game = Game([])
        players = []

        # Deal all cards out, one to each of 94 players so that none can go bust.
        for x in range(94):
            p = Player(game)
            players.append(p)
            p.ReceiveCard(self.Deck.DealCard())

        self.assertEqual(0, self.Deck.GetNumRemaining())

        # Add all the players to the game and then end the round.
        game.AddPlayers(players)
        for p in players:
            self.Deck.CollectDiscards(p.RoundEnd())

        self.Deck.Shuffle()

        # 88 because the 6 total Fr and F3 cards are handled by Game.PlayerTurn() method. Tested seperatedly below.
        self.assertEqual(88, self.Deck.GetNumRemaining())

    def test_discard_collection_Fr_F3(self):
        predefined_deck = GameDeck(["F3", "+2", "#2", "Fr"])
        player = Player()
        game = Game([player], predefined_deck)

        # Begin with 4 cards in deck, including a Freeze and a Flip3
        self.assertEqual(4, predefined_deck.GetNumRemaining())

        # Player draws a Flip3, resulting in them playing a Freeze.
        game.PlayerTurn(player)

        # Ensure all cards have been played from deck.
        self.assertEqual(0, predefined_deck.GetNumRemaining())

        predefined_deck.CollectDiscards(player.RoundEnd())

        # Collected and shuffle all cards back together, check that all 3 Freeze and Flip 3 are back in the deck.
        predefined_deck.Shuffle()
        self.assertEqual(94, predefined_deck.GetNumRemaining())
        self.assertEqual(3, predefined_deck.GetRemainingCards()["Fr"])
        self.assertEqual(3, predefined_deck.GetRemainingCards()["F3"])

class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.game = Game([])
        self.player = Player(self.game)
        self.game.AddPlayers([self.player])

    def test_NewRound(self):
        self.assertEqual(self.player.GetGameScore(), 0)
        self.assertEqual(self.player.GetHandScore(), 0)
        self.assertEqual(self.player.IsActive(), True)
        self.assertEqual(self.player.GetHandDict(), {   
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
        })

    def test_TakeTurn(self):
        while self.player.TakeTurn():
            self.assertEqual(self.player.IsActive(), True)
        self.assertEqual(self.player.IsActive(), False)

    def test_ReceiveCard_passed(self):
        while self.player.TakeTurn():
            self.assertEqual(self.player.IsActive(), True)
        self.assertEqual(self.player.IsActive(), False)

        with self.assertRaises(Exception) as context:
            self.player.ReceiveCard("SC")

        self.assertEqual(str(context.exception), "I have already passed.")

    def test_ReceiveCard_frozen(self):
        self.player.GetsFrozen()

        with self.assertRaises(Exception) as context:
            self.player.ReceiveCard("SC")

        self.assertEqual(str(context.exception), "I have already been frozen.")

    def test_ReceiveCard_Num1(self):
        self.player.ReceiveCard("#2")
        self.assertEqual(self.player.GetHandDict()["#2"], 1)
        self.assertEqual(self.player.IsActive(), True)
        self.assertEqual(self.player.GetHandScore(), 2)

        self.player.ReceiveCard("#10")
        self.assertEqual(self.player.GetHandDict()["#2"], 1)
        self.assertEqual(self.player.GetHandDict()["#10"], 1)
        self.assertEqual(self.player.IsActive(), True)
        self.assertEqual(self.player.GetHandScore(), 12)

        self.player.ReceiveCard("#2")
        self.assertEqual(self.player.GetHandDict()["#2"], 2)
        self.assertEqual(self.player.GetHandDict()["#10"], 1)
        self.assertEqual(self.player.IsActive(), False)
        self.assertEqual(self.player.GetHandScore(), 0)

        with self.assertRaises(Exception) as context:
            self.player.ReceiveCard("#2")

        self.assertEqual(str(context.exception), "I am already bust.")

    def test_ReceiveCard_Num2(self):
        self.player.ReceiveCard("#12")
        self.assertEqual(self.player.GetHandDict()["#12"], 1)
        self.assertEqual(self.player.IsActive(), True)
        self.assertEqual(self.player.GetHandScore(), 12)

        self.player.ReceiveCard("+2")
        self.assertEqual(self.player.GetHandDict()["#12"], 1)
        self.assertEqual(self.player.GetHandDict()["+2"], 1)
        self.assertEqual(self.player.IsActive(), True)
        self.assertEqual(self.player.GetHandScore(), 14)

        self.player.ReceiveCard("#12")
        self.assertEqual(self.player.GetHandDict()["#12"], 2)
        self.assertEqual(self.player.GetHandDict()["+2"], 1)
        self.assertEqual(self.player.IsActive(), False)
        self.assertEqual(self.player.GetHandScore(), 0)

        with self.assertRaises(Exception) as context:
            self.player.ReceiveCard("#2")

        self.assertEqual(str(context.exception), "I am already bust.")

    def test_ReceiveCard_Fr(self):
        self.player.ReceiveCard("#12")
        self.assertEqual(self.player.GetHandDict()["#12"], 1)
        self.assertEqual(self.player.IsActive(), True)
        self.assertEqual(self.player.GetHandScore(), 12)

        self.player.ReceiveCard("+2")
        self.assertEqual(self.player.GetHandDict()["#12"], 1)
        self.assertEqual(self.player.GetHandDict()["+2"], 1)
        self.assertEqual(self.player.IsActive(), True)
        self.assertEqual(self.player.GetHandScore(), 14)

        response = self.player.ReceiveCard("Fr")
        self.assertEqual(self.player.GetHandDict()["#12"], 1)
        self.assertEqual(self.player.GetHandDict()["+2"], 1)
        self.assertEqual(response, self.player) # There is only one player in game, so they must choose themselves.

    def test_GetsFrozen(self):
        self.player.GetsFrozen()
        self.assertEqual(self.player.IsActive(), False)
        self.assertEqual(self.player.GetHandDict()["Fr"], 1)

        with self.assertRaises(Exception) as context:
            self.player.GetsFrozen()

        self.assertEqual(str(context.exception), "I have already been frozen.")

    def test_ReceiveCard_F3(self):
        self.player.ReceiveCard("#12")
        self.assertEqual(self.player.GetHandDict()["#12"], 1)
        self.assertEqual(self.player.IsActive(), True)
        self.assertEqual(self.player.GetHandScore(), 12)

        self.player.ReceiveCard("+10")
        self.assertEqual(self.player.GetHandDict()["#12"], 1)
        self.assertEqual(self.player.GetHandDict()["+10"], 1)
        self.assertEqual(self.player.IsActive(), True)
        self.assertEqual(self.player.GetHandScore(), 22)

        response = self.player.ReceiveCard("F3")
        self.assertEqual(self.player.GetHandDict()["#12"], 1)
        self.assertEqual(self.player.GetHandDict()["+10"], 1)
        self.assertEqual(response, self.player) # There is only one player in game, so they must choose themselves.

    # Test that SC allows player to survive busting.
    def test_ReceiveCard_SC1(self):
        self.player.ReceiveCard("SC")
        self.assertEqual(self.player.GetHandDict()["SC"], 1)
        self.assertEqual(self.player.IsActive(), True)

        self.player.ReceiveCard("#12")
        self.assertEqual(self.player.GetHandDict()["#12"], 1)
        self.assertEqual(self.player.GetHandDict()["SC"], 1)

        self.player.ReceiveCard("#12")
        self.assertEqual(self.player.IsActive(), True)
        self.assertEqual(self.player.GetHandDict()["#12"], 1)
        self.assertEqual(self.player.GetHandDict()["SC"], 0)

    # Test that player gives a SC to another player that doesn't have one.
    def test_ReceiveCard_SC2(self):
        self.player2 = Player(self.game)
        self.game.AddPlayers([self.player2])

        self.player.ReceiveCard("SC")
        self.assertEqual(self.player.GetHandDict()["SC"], 1)

        response = self.player.ReceiveCard("SC")
        self.assertEqual(self.player.GetHandDict()["SC"], 1)
        self.assertEqual(response, self.player2) # Player 2 has no SC so they are given it.

    # Test that player discards a SC that cannot be allocated to another player.
    def test_ReceiveCard_SC3(self):
        self.player.ReceiveCard("SC")
        self.assertEqual(self.player.GetHandDict()["SC"], 1)

        response = self.player.ReceiveCard("SC")
        self.assertEqual(self.player.GetHandDict()["SC"], 1)
        self.assertEqual(response, None) # There is no player without a SC so they discard it.

    # Test that player discards a SC that cannot be allocated to another player.
    def test_ReceiveCard_SC4(self):
        self.player2 = Player(self.game)
        self.game.AddPlayers([self.player2])

        response = self.player.ReceiveCard("SC")
        self.assertEqual(response, None) # They player keeps the SC, no player should be selected.
        self.assertEqual(self.player.GetHandDict()["SC"], 1)

        response = self.player.ReceiveCard("SC")
        self.assertEqual(self.player.GetHandDict()["SC"], 1)
        self.assertEqual(response, self.player2) # Player 2 has no SC so they are given it.

    def test_CalculateScore(self):
        self.player.ReceiveCard("#4")
        self.player.ReceiveCard("#0")
        self.player.ReceiveCard("#1")

        self.assertEqual(self.player.CalculateHandScore(), 5)

        self.player.ReceiveCard("+6")

        self.assertEqual(self.player.CalculateHandScore(), 11)

        self.player.ReceiveCard("SC")     
        self.player.ReceiveCard("X2")

        self.assertEqual(self.player.CalculateHandScore(), 16)

        self.player.ReceiveCard("#4")
        self.assertEqual(self.player.CalculateHandScore(), 16)

        self.player.ReceiveCard("#4")
        self.assertEqual(self.player.CalculateHandScore(), 0)

    def test_CalculateScore_Flip7(self):
        self.player.ReceiveCard("#1")
        self.player.ReceiveCard("#2")
        self.player.ReceiveCard("#3")
        self.player.ReceiveCard("#4")
        self.player.ReceiveCard("#5")
        self.player.ReceiveCard("#6")

        self.assertEqual(self.player.CalculateHandScore(), 21)

        self.player.ReceiveCard("X2")

        self.assertEqual(self.player.CalculateHandScore(), 42)

        self.player.ReceiveCard("#0")

        self.assertEqual(self.player.CalculateHandScore(), 57)

class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = Game([])
        self.player1 = Player(self.game)
        self.player2 = Player(self.game)
        self.player3 = Player(self.game)

        self.game.AddPlayers([self.player1, self.player2, self.player3])

    # Test that a card is correctly dealt to a player when 
    def test_PlayerTurn_Num1(self):
        self.assertEqual(self.player1.GetGameScore(), 0)

        self.game.PlayerTurn(self.player1, "#2")

        self.assertEqual(sum(self.player1.GetHandDict().values()), 1)
        self.assertEqual(self.player1.GetHandDict()["#2"], 1)
        self.assertEqual(self.player1.GetHandScore(), 2)

    # Test that a player busts when using Player Turn
    def test_PlayerTurn_Num2(self):
        self.assertEqual(self.player1.GetGameScore(), 0)

        self.game.PlayerTurn(self.player1, "#2")
        self.game.PlayerTurn(self.player1, "#10")
        self.game.PlayerTurn(self.player1, "#2")

        self.assertEqual(sum(self.player1.GetHandDict().values()), 3)
        self.assertEqual(self.player1.GetHandDict()["#10"], 1)
        self.assertEqual(self.player1.GetHandDict()["#2"], 2)
        self.assertEqual(self.player1.GetHandScore(), 0)
        self.assertEqual(self.player1.IsActive(), False)

    def test_PlayerTurn_Fr(self):
        chosen = self.game.PlayerTurn(self.player1, "Fr")

        if chosen == self.player1:
            self.assertEqual(sum(self.player1.GetHandDict().values()), 1)
        else:
            self.assertEqual(sum(self.player1.GetHandDict().values()), 0)

        # Someone has been frozen.
        self.assertEqual(self.player1.IsActive() and self.player2.IsActive() and self.player3.IsActive(), False)

    def test_PlayerTurn_F3_1(self):
        self.game.SetDeck(GameDeck(["F3", "#0", "#1", "#2"]))
        chosen = self.game.PlayerTurn(self.player1)

        self.assertEqual(chosen.GetHandDict()["#0"], 1)
        self.assertEqual(chosen.GetHandDict()["#1"], 1)
        self.assertEqual(chosen.GetHandDict()["#2"], 1)

        if chosen == self.player1:
            self.assertEqual(sum(self.player1.GetHandDict().values()), 3)
        else:
            self.assertEqual(sum(self.player1.GetHandDict().values()), 0)

    def test_PlayerTurn_F3_2(self):
        self.game.SetDeck(GameDeck(["F3", "Fr", "#2", "#2"]))
        chosen = self.game.PlayerTurn(self.player1)

        self.assertEqual(chosen.GetHandDict()["#2"], 2)

        # Nobody has been frozen since the Freeze should not be played.
        self.assertEqual(self.player1.IsFrozen() or self.player2.IsFrozen() or self.player3.IsFrozen(), False)

    def test_PlayerTurn_F3_F3_F3_F3(self):
        self.game.SetDeck(GameDeck(["F3", "F3", "F3", "F3", "#0", "#1", "+2", "#3", "+4", "#5", "+6", "#7", "#8"]))
        self.game.PlayerTurn(self.player1)

        dealt_cards = self.player1.hand.copy()
        for player in [self.player2, self.player3]:
            for card in player.hand.keys():
                dealt_cards[card] += player.hand[card]

        # Someone has been frozen.
        self.assertEqual(self.player1.IsFrozen() and self.player2.IsFrozen() and self.player3.IsFrozen(), False)
    #def test_PlayRound(self):
        
    # Test that Flipping 7 works.
    # Test that an SC, Fr, F3 that is given to another player is added to their hand.

    def test_PlayGame(self):
        self.game.PlayGame()

class TestPredictivePlayer(unittest.TestCase):

    def setUp(self):
        self.player = PredictivePlayer()
        self.game = Game([self.player])

    def test_TakeTurn(self):
        while self.player.TakeTurn():
            self.assertEqual(self.player.IsActive(), True)
        self.assertEqual(self.player.IsActive(), False)

if __name__ == '__main__':
    unittest.main()
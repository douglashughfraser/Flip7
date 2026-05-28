import random

class GameDeck:

    AllCards = {   
        "#12": 12,
        "#11": 11,
        "#10": 10,
        "#9": 9,
        "#8": 8,
        "#7": 7,
        "#6": 6,
        "#5": 5,
        "#4": 4,
        "#3": 3,
        "#2": 2,
        "#1": 1,
        "#0": 1,
        "SC": 3,
        "Fr": 3,
        "F3": 3,
        "+2": 1,
        "+4": 1,
        "+6": 1,
        "+8": 1,
        "+10": 1,
        "X2": 1,
    }

    def __init__(self, cards=None):
        if cards!=None:
            # If passed a dictionary, modify the default deck accordingly.
            if isinstance(cards, dict):
                self.AllCards = cards
        
        self.RemainingCards = self.AllCards.copy()
        
        self.DiscardCards = self.AllCards.copy()
        for card in self.AllCards.keys():
            self.DiscardCards[card] = 0

        self.total = 0
        self.top = 0

        self.deck = []
        self.Shuffle()

        # For testing, pass a predefined sequence of cards.
        if isinstance(cards, list):
            self.deck = cards

            # Discard all remaining cards so that only the predefined list remains.
            self.DiscardCards = self.RemainingCards.copy()
            for card in self.AllCards.keys():
                self.RemainingCards[card] = 0

            # Add predefined cards to RemainingCards dictionary. Remove from DiscardCards dictionary.
            # All predefined cards are now the only cards in the deck, the rest of the deck sits in the discard pile.
            # On a shuffle, exactly one full deck should be present again.
            for card in self.deck:
                self.RemainingCards[card] += 1
                self.DiscardCards[card] -= 1
    
    # Wipes the list of cards.
    # Reconstructs the deck list from the dictionary of remaining and discarded cards.
    # Shuffles that new list.
    def Shuffle(self):

        self.deck = []
        for card in self.AllCards.keys():
            self.deck += [card]*self.RemainingCards[card]
            self.deck += [card]*self.DiscardCards[card]

            self.RemainingCards[card] += self.DiscardCards[card]
            self.DiscardCards[card] = 0

        random.shuffle(self.deck)
        self.total = sum(self.RemainingCards.values())
        self.top = 0;

    def GetRemainingCards(self):
        return self.RemainingCards.copy()

    def GetAllCards(self):
        return self.AllCards.copy()

    def GetDiscardCards(self):
        return self.DiscardCards.copy()

    # Returns the number of cards remaining the deck.
    def GetNumRemaining(self):
        return sum(self.GetRemainingCards().values())

    # Print a list of strings denoting the current order of the deck.
    def GetCards(self):
        return self.deck

    # Accepts a list of strings containing card for the discard pile.
    # Use at the end of each round.
    # These cards are added in during the next shuffle.
    def CollectDiscards(self, discards):
        for card, count in discards.items():
            if card in self.DiscardCards.keys():
                self.DiscardCards[card] += count
            else:
                raise Exception(f'Unknown card {card} collected.')

    # Returns a string representing the top card of the deck. 
    # Shuffles deck if the returned card was the last card.
    def DealCard(self):

        if self.top == self.total:
            self.Shuffle()

        card = self.deck[self.top]
        self.top+=1

        self.RemainingCards[card] -= 1

        return card
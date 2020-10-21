from Deck import *
from Card import *

class Player:
    def __init__(self, index, cards):
        self.hand = arcade.SpriteList()
        self.hand.extend(cards)
        self.index = index

    def isHandFull(self):
        return len(self.hand) >= 6

    def FillHand(self, deck: Deck):
        while not self.isHandFull() and any(deck.card_list):
            crd = deck.GetCard()
            crd.face_up()
            crd.angle = 0
            self.hand.append(crd)
            self.SortHand()

    def SortHand(self):
        for i in range(len(self.hand) - 1):
            for j in range(len(self.hand) - i - 1):
                if self.hand[j].suit > self.hand[j+1].suit:
                    self.hand[j], self.hand[j+1] = self.hand[j+1], self.hand[j]
                if self.hand[j].suit == self.hand[j + 1].suit:
                    if self.hand[j].RankIndex() > self.hand[j + 1].RankIndex():
                        self.hand[j], self.hand[j+1] = self.hand[j+1], self.hand[j]
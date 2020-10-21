from Card import *
import arcade
import random


class Deck:
    def __init__(self):
        self.card_list = arcade.SpriteList()
        self.FillDeck()
    
    def FillDeck(self):
        for card_suit in CARD_SUITS:
            for card_value in CARD_VALUES:
                card = Card(card_suit, card_value, CARD_SCALE)
                card.position = START_X, BOTTOM_Y
                self.card_list.append(card)
        random.shuffle(self.card_list)

    def Count(self):
        return len(self.card_list)

    def GetCard(self):
        if len(self.card_list) > 0:
            return self.card_list.pop()

    def PutBottom(self, card):
        self.card_list.insert(0, card)

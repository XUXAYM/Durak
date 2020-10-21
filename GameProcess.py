from Player import *
from Deck import *
from Card import *


class GameProcess:
    # константы результатов хода
    NORMAL = 'normal'
    TOOK_CARDS = 'took_cards'
    TIE = 'tie'
    GAME_OVER = 'game_over'

    def __init__(self, playerCount, parent):
        self.deck = Deck()
        self.parent = parent
        self.roundStep = ATACK_ROUND
        self.playerCount = playerCount
        self.players = []
        for i in range(playerCount):
            plr = Player(i, [])
            plr.FillHand(self.deck)
            self.players.append(plr)

        self.trump = self.deck.GetCard()
        self.trump: Card
        self.deck.PutBottom(self.trump)

        self.atackList = []
        self.defendList = []

        self.attackerIndex = 0
        self.winner = None

        self.show_splitter = False
        self.turnDownButton = False
        self.takeAllButton = False
        self.nextPlayerButton = False
        self.botTurn = False

    def BotAtack(self):
        assert not self.winner

        if len(self.CurrentPlayer.hand) == 0:
            self.botTurn = False
            self.parent.finish_round()
            return
        minCard = None
        for crd in self.CurrentPlayer.hand:
            if crd.suit is not self.trump.suit:
                if self.isAddableToField(crd):
                    if minCard is None:
                        minCard = crd
                    elif crd.rank <= minCard.rank:
                        minCard = crd
        if minCard is None:
            for crd in self.CurrentPlayer.hand:
                if self.isAddableToField(crd):
                    if minCard is None:
                        minCard = crd
                    elif crd.rank <= minCard.rank:
                        minCard = crd
        try:
            minCard.face_up()
            for i in range(PILE_COUNT):
                if len(self.parent.piles[i]) == 0:
                    pile = self.parent.pile_mat_list[i]
                    minCard.position = pile.center_x, pile.center_y
                    self.parent.piles[i].append(minCard)
                    self.atackList.append(minCard)
                    self.CurrentPlayer.hand.remove(minCard)
                    self.botTurn = False
                    self.takeAllButton = True
                    self.parent.swap_player_draw()
                    self.parent.ui_manager.add_ui_element(self.parent.take_button)
                    break
        except:
            self.botTurn = False
            self.parent.finish_round()
            return

    def BotDefend(self):
        assert not self.winner

        if len(self.defendList) == len(self.atackList):
            return

        if len(self.OpponentPlayer.hand) == 0:
            return

        for crdA in self.atackList:
            defendCrd = None
            for crdD in self.OpponentPlayer.hand:
                if self.isCardCanBeat(crdD, crdA):
                    if crdD.suit is not self.trump.suit:
                        if defendCrd is None:
                            defendCrd = crdD
                        elif defendCrd.rank > crdD.rank:
                            defendCrd = crdD
            if defendCrd is None:
                for crdD in self.OpponentPlayer.hand:
                    if self.isCardCanBeat(crdD, crdA):
                        if defendCrd is None:
                            defendCrd = crdD
                        elif defendCrd.rank > crdD.rank:
                            defendCrd = crdD

            pile, distance = arcade.get_closest_sprite(crdA, self.parent.pile_mat_list)
            pile_index = self.parent.pile_mat_list.index(pile)
            if len(self.parent.piles[pile_index]) == 1:
                try:
                    defendCrd.face_up()
                except:
                    self.botTurn = False
                    self.parent.finish_round()
                    return

                defendCrd.position = pile.center_x, pile.center_y - CARD_VERTICAL_OFFSET
                self.parent.piles[pile_index].append(defendCrd)
                self.defendList.append(defendCrd)
                self.OpponentPlayer.hand.remove(defendCrd)

        if len(self.defendList) != len(self.atackList):
            self.botTurn = False
            self.parent.finish_round()
        else:
            self.botTurn = False
            self.parent.swap_player_draw()
            self.parent.ui_manager.add_ui_element(self.parent.finish_turn_button)

    def Attack(self, card):
        assert not self.winner
        if not self.isAddableToField(card):
            return False
        cur, opp = self.CurrentPlayer, self.OpponentPlayer
        cur.hand.remove(card)
        self.nextPlayerButton = True
        self.parent.ui_manager.purge_ui_elements()
        self.parent.ui_manager.add_ui_element(self.parent.next_button)
        return True

    def isAddableToField(self, card):
        if not self.atackList and not self.defendList:
            return True
        for attackCard in self.atackList:
            if self.isCardMatch(attackCard, card):
                return True
        for defendCard in self.defendList:
            if self.isCardMatch(defendCard, card):
                return True
        return False
    
    def isCardMatch(self, card1: Card, card2: Card):
        if card1 is None or card2 is None:
            return False
        return card1.rank == card2.rank

    def Defend(self, defendingCard, attackingCard):
        assert not self.winner
        if len(self.defendList) == len(self.atackList):
            return False
        if self.isCardCanBeat(defendingCard, attackingCard):
            self.defendList.append(defendingCard)
            self.OpponentPlayer.hand.remove(defendingCard)
            return True
        return False
    
    def isCardCanBeat(self, defendingCard , attackingCard):
        if defendingCard.suit == attackingCard.suit:
            if defendingCard.RankIndex() > attackingCard.RankIndex():
                return True
            else:
                return False
        elif defendingCard.suit == self.trump.suit:
            return True
        else:
            return False
    
    @property
    def AnyUnbeatenCard(self):
        return any(c is None for c in self.defendList)
    
    @property
    def CurrentPlayer(self):
        return self.players[self.attackerIndex]

    @property
    def OpponentPlayer(self):
        return self.players[(self.attackerIndex + 1) % self.playerCount]
    
    @property
    def isAttackSucceed(self):
        if len(self.defendList) < len(self.atackList):
            return True
        else:
            return False

    def isCanAtack(self):
        for crd in self.CurrentPlayer.hand:
            if self.isAddableToField(crd):
                return True
        return False
    
    def FinishTurn(self):
        assert not self.winner
        tookCards = False
        if self.isAttackSucceed:
            self.TakeAll()
            tookCards = True
        else:
            self.atackList = []
            self.defendList = []
        for p in self.Rotate(self.players, self.attackerIndex):
            p: Player
            p.FillHand(self.deck)
        if not any(self.deck.card_list):
            for p in self.players:
                p: Player
                if len(self.CurrentPlayer.hand) == 0 and len(self.OpponentPlayer.hand) == 0:
                    return self.TIE
                if len(p.hand) == 0:
                    self.winner = p.index
                    return self.GAME_OVER
        if tookCards:
            return self.TOOK_CARDS
        else:
            self.attackerIndex = self.OpponentPlayer.index
            print(self.attackerIndex)
            return self.NORMAL

    def TakeAll(self):
        cards = self.atackList + self.defendList
        self.OpponentPlayer.hand.extend(cards)
        self.OpponentPlayer.SortHand()
        self.atackList = []
        self.defendList = []

    def Rotate(self, l, n):
        return l[n:] + l[:n]
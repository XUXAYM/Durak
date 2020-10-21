# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import time
from GameProcess import *
from Render import *
import arcade.gui
from arcade.gui import UIManager

class StartGameWithPlayerButton(arcade.gui.UIFlatButton):
    def __init__(self, center_x, center_y, parent):
        super().__init__('Играть с другим игроком', font_size=32, center_x=center_x+5, center_y=center_y+40, width=400, height=80)
        self.parent = parent

    def on_click(self):
        self.parent.ui_manager.purge_ui_elements()
        game_view = GameView()
        game_view.setup()
        self.parent.window.show_view(game_view)

class StartGameWithBotButton(arcade.gui.UIFlatButton):
    def __init__(self, center_x, center_y, parent):
        super().__init__('Играть с компьютером', font_size=32, center_x=center_x+5, center_y=center_y, width=400, height=80)
        self.parent = parent

    def on_click(self):
        self.parent.ui_manager.purge_ui_elements()
        game_view = GameBotView()
        game_view.setup()
        self.parent.window.show_view(game_view)

class ExitButton(arcade.gui.UIFlatButton):
    def __init__(self, center_x, center_y):
        super().__init__('Выход из игры', font_size=32, center_x=center_x+5, center_y=center_y, width=400, height=80)

    def on_click(self):
        os.abort()

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = UIManager()
        self.start_with_player = StartGameWithPlayerButton(SCREEN_WIDTH/2, SCREEN_HEIGHT/2+50, self)
        self.start_with_bot = StartGameWithBotButton(SCREEN_WIDTH/2, SCREEN_HEIGHT/2-40, self)
        self.exit = ExitButton(SCREEN_WIDTH/2, SCREEN_HEIGHT/2-170)
        self.ui_manager.add_ui_element(self.start_with_player)
        self.ui_manager.add_ui_element(self.start_with_bot)
        self.ui_manager.add_ui_element(self.exit)

    def on_show(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Дурак", SCREEN_WIDTH/2, SCREEN_HEIGHT/2+180,
                         arcade.color.BLACK, font_size=50, anchor_x="center")

class SplitView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Сменить игрока", SCREEN_WIDTH/2, SCREEN_HEIGHT/2,
                         arcade.color.GRAY, font_size=50, anchor_x="center")
        arcade.draw_text("Нажмите любую кнопку", SCREEN_WIDTH/2, SCREEN_HEIGHT/2-75,
                         arcade.color.GRAY, font_size=20, anchor_x="center")

    def on_key_press(self, symbol: int, modifiers: int):
        arcade.set_background_color(arcade.color.AMAZON)
        if self.game_view.game.takeAllButton == True:
            self.game_view.ui_manager.add_ui_element(self.game_view.take_button)
        if self.game_view.game.turnDownButton == True:
            self.game_view.ui_manager.add_ui_element(self.game_view.finish_turn_button)
        self.window.show_view(self.game_view)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        arcade.set_background_color(arcade.color.AMAZON)
        if self.game_view.game.takeAllButton == True:
            self.game_view.ui_manager.add_ui_element(self.game_view.take_button)
        if self.game_view.game.turnDownButton == True:
            self.game_view.ui_manager.add_ui_element(self.game_view.finish_turn_button)
        self.window.show_view(self.game_view)

class FinishDefendButton(arcade.gui.UIFlatButton):
    def __init__(self, center_x, center_y, parent):
        super().__init__('Взять', center_x=center_x+5, center_y=center_y+40, width=80, height=40)
        self.parent = parent

    def on_click(self):
        if self.parent.game.takeAllButton == True:
            self.parent.ui_manager.purge_ui_elements()
            self.parent.game.botTurn = True
            self.parent.game.takeAllButton = False
            self.parent.finish_round()
            self.parent.game.show_splitter = True

class FinishAtackButton(arcade.gui.UIFlatButton):
    def __init__(self, center_x, center_y, parent):
        super().__init__('Бито', center_x=center_x, center_y=center_y-40, width=70, height=40)
        self.parent = parent

    def on_click(self):
        if self.parent.game.turnDownButton == True:
            self.parent.ui_manager.purge_ui_elements()
            self.parent.game.botTurn = True
            self.parent.finish_round()
            self.parent.game.show_splitter = True
            self.parent.game.turnDownButton = False

class NextPlayerButton(arcade.gui.UIFlatButton):
    def __init__(self, center_x, center_y, parent):
        super().__init__('Передать ход', center_x=center_x+65, center_y=center_y, width=200, height=40)
        self.parent = parent

    def on_click(self):
        if self.parent.game.nextPlayerButton == True:
            self.parent.ui_manager.purge_ui_elements()
            self.parent.game.botTurn = True
            self.parent.swap_player_draw()
            self.parent.game.nextPlayerButton = False
            self.parent.game.show_splitter = True

class GameView(arcade.View):

    def __init__(self):
        super().__init__()

        arcade.set_background_color(arcade.color.AMAZON)
        self.game = GameProcess(2, self)
        self.deck = self.game.deck

        self.ui_manager = UIManager()

        self.held_cards = None

        self.held_cards_original_position = None

        self.pile_mat_list = None


    def setup(self):
        self.card_list = self.deck.card_list

        for card in self.card_list:
            card.position = START_X, MIDDLE_Y

        self.card_list[0].position = START_X+20, MIDDLE_Y
        self.card_list[0].angle = 90
        self.card_list[0].face_up()

        self.finish_turn_button = FinishAtackButton(START_X, BOTTOM_Y, self)
        self.take_button = FinishDefendButton(START_X, BOTTOM_Y, self)
        self.next_button = NextPlayerButton(START_X, BOTTOM_Y, self)

        self.current_player_label = arcade.gui.UILabel(
            f'Ход \nигрока {self.game.CurrentPlayer.index}',
            center_x=SCREEN_WIDTH - START_X*1.5,
            center_y=MIDDLE_Y,
        )

        self.ui_manager.add_ui_element(self.current_player_label)

        self.next_button.stop()

        self.card_counter = arcade.text

        self.current_player_hand = self.game.CurrentPlayer.hand
        self.opponent_player_hand = self.game.OpponentPlayer.hand

        self.redraw_hand()
        self.redraw_opp_hand()

        self.held_cards = []

        self.held_cards_original_position = []

        self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

        for i in range(PILE_COUNT):
            self.pile_mat_list.append(arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN))
        self.pile_mat_list[TOP_ROW_PILE_1].position = (MIDDLE_X - MAT_WIDTH / 2) - X_SPACING, MIDDLE_Y
        self.pile_mat_list[TOP_ROW_PILE_2].position = (MIDDLE_X - MAT_WIDTH / 2), MIDDLE_Y
        self.pile_mat_list[TOP_ROW_PILE_3].position = (MIDDLE_X - MAT_WIDTH / 2) + X_SPACING, MIDDLE_Y
        self.pile_mat_list[TOP_ROW_PILE_4].position = (MIDDLE_X - MAT_WIDTH / 2) + (2 * X_SPACING), MIDDLE_Y
        self.pile_mat_list[BOTTOM_ROW_PILE_1].position = (MIDDLE_X - MAT_WIDTH / 2) - X_SPACING, MIDDLE_Y - MAT_HEIGHT
        self.pile_mat_list[BOTTOM_ROW_PILE_2].position = (MIDDLE_X - MAT_WIDTH / 2), MIDDLE_Y - MAT_HEIGHT
        self.pile_mat_list[BOTTOM_ROW_PILE_3].position = (MIDDLE_X - MAT_WIDTH / 2) + X_SPACING, MIDDLE_Y - MAT_HEIGHT
        self.pile_mat_list[BOTTOM_ROW_PILE_4].position = (MIDDLE_X - MAT_WIDTH / 2) + (2 * X_SPACING), MIDDLE_Y - MAT_HEIGHT

        self.piles = []
        for i in range(PILE_COUNT):
            self.piles.append(arcade.SpriteList())

    def on_draw(self):
        arcade.start_render()
        if self.game.winner is None:
            self.pile_mat_list.draw()
            for pile in self.piles:
                pile.draw()
            self.ui_manager.on_draw()
            self.card_list.draw()
            self.card_counter.render_text(arcade.CreateText(str(self.deck.Count()), (0, 0, 0), 20, 50), START_X - 15, MIDDLE_Y - MAT_HEIGHT/1.5)
            self.current_player_label.draw()
            self.current_player_hand.draw()
            self.opponent_player_hand.draw()
        else:
            self.window.show_view(GameOverView(self))

    def update(self, delta_time):
        if self.game.show_splitter:
            self.game.show_splitter = False
            self.window.show_view(SplitView(self))

    def redraw_hand(self):
        count = len(self.current_player_hand)
        new_middle_x = MIDDLE_X - CARD_HORIZONTAL_OFFSET * (count)/2
        i = 0
        for card in self.current_player_hand:
            card.position = new_middle_x + i, BOTTOM_Y
            i += CARD_HORIZONTAL_OFFSET
            card.face_up()

    def redraw_opp_hand(self):
        count = len(self.opponent_player_hand)
        new_middle_x = MIDDLE_X - CARD_HORIZONTAL_OFFSET * (count)/2
        i = 0
        for card in self.opponent_player_hand:
            card.position = new_middle_x + i, SCREEN_HEIGHT - BOTTOM_Y
            i += CARD_HORIZONTAL_OFFSET
            card.face_down()

    def show_top(self, card):
        self.index = self.current_player_hand.index(card)
        for i in range(self.index, len(self.current_player_hand) - 1):
            self.current_player_hand[i] = self.current_player_hand[i + 1]
        self.current_player_hand[len(self.current_player_hand) - 1] = card

    def return_down(self, card):
        for i in range(len(self.current_player_hand) - 1, self.index, -1):
            self.current_player_hand[i] = self.current_player_hand[i-1]
        self.current_player_hand[self.index] = card

    def finish_round(self):
        result = self.game.FinishTurn()
        self.redraw_hand()
        self.redraw_opp_hand()
        self.piles = []
        for i in range(PILE_COUNT):
            self.piles.append(arcade.SpriteList())
        if result == self.game.NORMAL:
            self.current_player_hand = self.game.CurrentPlayer.hand
            self.opponent_player_hand = self.game.OpponentPlayer.hand
            self.game.roundStep = ATACK_ROUND
            self.redraw_hand()
            self.redraw_opp_hand()
            self.current_player_label.text = f'Ход \nигрока {self.game.CurrentPlayer.index}'
        elif result == self.game.TOOK_CARDS:
            self.current_player_hand = self.game.CurrentPlayer.hand
            self.opponent_player_hand = self.game.OpponentPlayer.hand
            self.game.roundStep = ATACK_ROUND
            self.redraw_hand()
            self.redraw_opp_hand()
            self.current_player_label.text = f'Ход \nигрока {self.game.CurrentPlayer.index}'
        elif result == self.game.TIE:
            endgame_label = arcade.gui.UILabel(
                'Ничья!',
                center_x= MIDDLE_X,
                center_y= MIDDLE_Y,
            )
            self.ui_manager.add_ui_element(endgame_label)
        elif result == self.game.GAME_OVER:
            self.window.show_view(GameOverView(self))

    def swap_player_draw(self):
        if self.game.roundStep == ATACK_ROUND:
            self.current_player_label.text = f'Ход \nигрока {self.game.OpponentPlayer.index}'
            self.current_player_hand = self.game.OpponentPlayer.hand
            self.opponent_player_hand = self.game.CurrentPlayer.hand
            self.game.roundStep = DEFEND_ROUND
            self.ui_manager.purge_ui_elements()
            self.game.nextPlayerButton = False
            self.game.turnDownButton = False
            self.game.takeAllButton = True
        else:
            self.current_player_hand = self.game.CurrentPlayer.hand
            self.opponent_player_hand = self.game.OpponentPlayer.hand
            self.current_player_label.text = f'Ход \nигрока {self.game.CurrentPlayer.index}'
            self.game.roundStep = ATACK_ROUND
            self.game.takeAllButton = False
            self.game.nextPlayerButton = False
            self.ui_manager.purge_ui_elements()
            self.game.turnDownButton = True
        self.redraw_hand()
        self.redraw_opp_hand()

    def on_mouse_press(self, x, y, button, key_modifiers):
        if self.game.winner is not None:
            return

        self.game.show_splitter = False

        cards = arcade.get_sprites_at_point((x, y), self.current_player_hand)

        if len(cards) > 0:
            primary_card = cards[-1]

            self.held_cards = [primary_card]
            self.held_cards_original_position = [self.held_cards[0].position]
            self.show_top(self.held_cards[0])

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        if self.game.winner is not None:
            return

        for card in self.held_cards:
            card.center_x += dx
            card.center_y += dy

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        if self.game.winner is not None:
            return

        if len(self.held_cards) == 0:
            return

        pile, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
        reset_position = True
        pile_index = self.pile_mat_list.index(pile)

        if arcade.check_for_collision(self.held_cards[0], pile) and self.game.roundStep == ATACK_ROUND and len(self.piles[pile_index]) == 0:
            if self.game.Attack(self.held_cards[0]):
                for i, dropped_card in enumerate(self.held_cards):
                    dropped_card.position = pile.center_x, pile.center_y
                self.piles[pile_index].append(self.held_cards[0])
                self.game.atackList.append(self.held_cards[0])
                self.card_list.draw()
                self.redraw_hand()
                self.redraw_opp_hand()
                self.game.turnDownButton = False

                reset_position = False
        elif arcade.check_for_collision(self.held_cards[0], pile) and self.game.roundStep == DEFEND_ROUND and len(self.piles[pile_index]) == 1:
            if self.piles[pile_index][0] in self.game.atackList:
                atack = self.game.atackList[self.game.atackList.index(self.piles[pile_index][0])]
            if self.game.Defend(self.held_cards[0], atack):
                for i, dropped_card in enumerate(self.held_cards):
                    dropped_card.position = pile.center_x, pile.center_y - CARD_VERTICAL_OFFSET
                self.piles[pile_index].append(self.held_cards[0])
                if len(self.game.atackList) == len(self.game.defendList):
                    self.ui_manager.purge_ui_elements()
                    self.game.nextPlayerButton = True
                    self.ui_manager.add_ui_element(self.next_button)
                    self.game.takeAllButton = False
                    self.redraw_hand()
                else:
                    self.redraw_hand()
                    self.redraw_opp_hand()
                reset_position = False

        if reset_position:
            for pile_index, card in enumerate(self.held_cards):
                card.position = self.held_cards_original_position[pile_index]
            self.return_down(self.held_cards[0])

        self.held_cards = []

class GameBotView(arcade.View):
        def __init__(self):
            super().__init__()
            arcade.set_background_color(arcade.color.AMAZON)
            self.game = GameProcess(2, self)
            self.deck = self.game.deck

            self.ui_manager = UIManager()

            self.held_cards = None

            self.held_cards_original_position = None

            self.pile_mat_list = None

        def setup(self):
            self.card_list = self.deck.card_list

            for card in self.card_list:
                card.position = START_X, MIDDLE_Y

            self.card_list[0].position = START_X + 20, MIDDLE_Y
            self.card_list[0].angle = 90
            self.card_list[0].face_up()

            self.finish_turn_button = FinishAtackButton(START_X, BOTTOM_Y, self)
            self.take_button = FinishDefendButton(START_X, BOTTOM_Y, self)
            self.next_button = NextPlayerButton(START_X, BOTTOM_Y, self)

            self.card_counter = arcade.text

            self.current_player_hand = self.game.CurrentPlayer.hand
            self.opponent_player_hand = self.game.OpponentPlayer.hand

            self.redraw_hand()
            self.redraw_opp_hand()

            self.held_cards = []

            self.held_cards_original_position = []

            self.pile_mat_list: arcade.SpriteList = arcade.SpriteList()

            for i in range(PILE_COUNT):
                self.pile_mat_list.append(
                    arcade.SpriteSolidColor(MAT_WIDTH, MAT_HEIGHT, arcade.csscolor.DARK_OLIVE_GREEN))
            self.pile_mat_list[TOP_ROW_PILE_1].position = (MIDDLE_X - MAT_WIDTH / 2) - X_SPACING, MIDDLE_Y
            self.pile_mat_list[TOP_ROW_PILE_2].position = (MIDDLE_X - MAT_WIDTH / 2), MIDDLE_Y
            self.pile_mat_list[TOP_ROW_PILE_3].position = (MIDDLE_X - MAT_WIDTH / 2) + X_SPACING, MIDDLE_Y
            self.pile_mat_list[TOP_ROW_PILE_4].position = (MIDDLE_X - MAT_WIDTH / 2) + (2 * X_SPACING), MIDDLE_Y
            self.pile_mat_list[BOTTOM_ROW_PILE_1].position = ( MIDDLE_X - MAT_WIDTH / 2) - X_SPACING, MIDDLE_Y - MAT_HEIGHT
            self.pile_mat_list[BOTTOM_ROW_PILE_2].position = (MIDDLE_X - MAT_WIDTH / 2), MIDDLE_Y - MAT_HEIGHT
            self.pile_mat_list[BOTTOM_ROW_PILE_3].position = (MIDDLE_X - MAT_WIDTH / 2) + X_SPACING, MIDDLE_Y - MAT_HEIGHT
            self.pile_mat_list[BOTTOM_ROW_PILE_4].position = (MIDDLE_X - MAT_WIDTH / 2) + (2 * X_SPACING), MIDDLE_Y - MAT_HEIGHT

            self.piles = []
            for i in range(PILE_COUNT):
                self.piles.append(arcade.SpriteList())

        def on_draw(self):
            arcade.start_render()
            if self.game.winner is None:
                self.pile_mat_list.draw()
                for pile in self.piles:
                    pile.draw()
                self.ui_manager.on_draw()
                self.card_list.draw()
                self.card_counter.render_text(arcade.CreateText(str(self.deck.Count()), (0, 0, 0), 20, 50), START_X - 15, MIDDLE_Y - MAT_HEIGHT/1.5)
                self.current_player_hand.draw()
                self.opponent_player_hand.draw()
            else:
                self.window.show_view(GameOverView(self))

        def redraw_hand(self):
            count = len(self.current_player_hand)
            new_middle_x = MIDDLE_X - CARD_HORIZONTAL_OFFSET * (count) / 2
            i = 0
            for card in self.current_player_hand:
                card.position = new_middle_x + i, BOTTOM_Y
                i += CARD_HORIZONTAL_OFFSET
                card.face_up()

        def redraw_opp_hand(self):
            count = len(self.opponent_player_hand)
            new_middle_x = MIDDLE_X - CARD_HORIZONTAL_OFFSET * (count) / 2
            i = 0
            for card in self.opponent_player_hand:
                card.position = new_middle_x + i, SCREEN_HEIGHT - BOTTOM_Y
                i += CARD_HORIZONTAL_OFFSET
                card.face_down()

        def show_top(self, card):
            self.index = self.current_player_hand.index(card)
            for i in range(self.index, len(self.current_player_hand) - 1):
                self.current_player_hand[i] = self.current_player_hand[i + 1]
            self.current_player_hand[len(self.current_player_hand) - 1] = card

        def return_down(self, card):
            for i in range(len(self.current_player_hand) - 1, self.index, -1):
                self.current_player_hand[i] = self.current_player_hand[i - 1]
            self.current_player_hand[self.index] = card

        def finish_round(self):
            result = self.game.FinishTurn()
            self.redraw_hand()
            self.redraw_opp_hand()
            self.piles = []
            for i in range(PILE_COUNT):
                self.piles.append(arcade.SpriteList())
            if result == self.game.NORMAL:
                self.game.roundStep = ATACK_ROUND
                self.redraw_hand()
                self.redraw_opp_hand()
                if self.game.botTurn == True:
                    self.game.BotAtack()
            elif result == self.game.TOOK_CARDS:
                self.game.roundStep = ATACK_ROUND
                self.redraw_hand()
                self.redraw_opp_hand()
                if self.game.botTurn == True:
                    self.game.BotAtack()
            elif result == self.game.TIE:
                endgame_label = arcade.gui.UILabel(
                    'Ничья!',
                    center_x=MIDDLE_X,
                    center_y=MIDDLE_Y,
                )
                self.ui_manager.add_ui_element(endgame_label)
            elif result == self.game.GAME_OVER:
                self.window.show_view(GameOverView(self))

        def swap_player_draw(self):
            if self.game.roundStep == ATACK_ROUND:
                self.game.roundStep = DEFEND_ROUND
                self.ui_manager.purge_ui_elements()
                if self.game.botTurn:
                    self.game.BotDefend()
                else:
                    self.game.takeAllButton = True
            else:
                self.game.roundStep = ATACK_ROUND
                self.game.takeAllButton = False
                self.game.nextPlayerButton = False
                self.ui_manager.purge_ui_elements()
                if self.game.botTurn:
                    self.game.BotAtack()
                else:
                    self.game.turnDownButton = True
            self.redraw_hand()
            self.redraw_opp_hand()

        def on_mouse_press(self, x, y, button, key_modifiers):
            if self.game.winner is not None:
                return

            if self.game.botTurn == True:
                return

            cards = arcade.get_sprites_at_point((x, y), self.current_player_hand)

            if len(cards) > 0:
                primary_card = cards[-1]

                self.held_cards = [primary_card]
                self.held_cards_original_position = [self.held_cards[0].position]
                self.show_top(self.held_cards[0])

        def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
            if self.game.winner is not None:
                return

            if self.game.botTurn == True:
                return

            for card in self.held_cards:
                card.center_x += dx
                card.center_y += dy

        def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
            if self.game.winner is not None:
                return

            if len(self.held_cards) == 0:
                return

            if self.game.botTurn == True:
                return

            pile, distance = arcade.get_closest_sprite(self.held_cards[0], self.pile_mat_list)
            reset_position = True
            pile_index = self.pile_mat_list.index(pile)
            if arcade.check_for_collision(self.held_cards[0], pile) and self.game.roundStep == ATACK_ROUND and len(self.piles[pile_index]) == 0:
                if self.game.Attack(self.held_cards[0]):
                    for i, dropped_card in enumerate(self.held_cards):
                        dropped_card.position = pile.center_x, pile.center_y
                    self.piles[pile_index].append(self.held_cards[0])
                    self.game.atackList.append(self.held_cards[0])
                    self.redraw_hand()
                    self.redraw_opp_hand()
                    self.game.turnDownButton = False
                    reset_position = False
            elif arcade.check_for_collision(self.held_cards[0], pile) and self.game.roundStep == DEFEND_ROUND and len(
                    self.piles[pile_index]) == 1:
                if self.piles[pile_index][0] in self.game.atackList:
                    defend = self.game.atackList[self.game.atackList.index(self.piles[pile_index][0])]
                if self.game.Defend(self.held_cards[0], defend):
                    for i, dropped_card in enumerate(self.held_cards):
                        dropped_card.position = pile.center_x, pile.center_y - CARD_VERTICAL_OFFSET
                    self.piles[pile_index].append(self.held_cards[0])
                    if len(self.game.atackList) == len(self.game.defendList):
                        self.ui_manager.purge_ui_elements()
                        if len(self.game.OpponentPlayer.hand) == 0:
                            time.sleep(5)
                            self.finish_round()
                            return
                        self.game.nextPlayerButton = True
                        self.ui_manager.add_ui_element(self.next_button)
                        self.game.takeAllButton = False
                        self.redraw_hand()
                    else:
                        self.redraw_hand()
                        self.redraw_opp_hand()
                    reset_position = False
            if reset_position:
                for pile_index, card in enumerate(self.held_cards):
                    card.position = self.held_cards_original_position[pile_index]
                self.return_down(self.held_cards[0])

            self.held_cards = []


class GameOverView(arcade.View):
    def __init__(self, parent):
        self.parent = parent
        super().__init__()

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
        arcade.draw_text("Игра окончена", 240, 400, arcade.color.WHITE, 54)
        arcade.draw_text("Нажмите любую кнопку,\nчтобы выйти в главное меню", 310, 300, arcade.color.WHITE, 32)
        output_total = f"Победитель: игрок {self.parent.game.winner}"
        arcade.draw_text(output_total, 10, 10, arcade.color.WHITE, 24)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Игра окончена", 200, 400, arcade.color.WHITE, 54)
        arcade.draw_text("Нажмите любую кнопку", 210, 300, arcade.color.WHITE, 32)
        output_total = f"Победитель: игрок {self.parent.game.winner}"
        arcade.draw_text(output_total, 10, 10, arcade.color.WHITE, 24)

    def on_key_press(self, symbol: int, modifiers: int):
        self.window.show_view(MenuView())

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        self.window.show_view(MenuView())

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.center_window()
    window.show_view(MenuView())
    arcade.run()

if __name__ == "__main__":
    main()
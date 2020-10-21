import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

CARD_SCALE = 0.6

CARD_WIDTH = 140 * CARD_SCALE
CARD_HEIGHT = 190 * CARD_SCALE

MAT_PERCENT_OVERSIZE = 1.0
MAT_HEIGHT = int(CARD_HEIGHT * MAT_PERCENT_OVERSIZE)
MAT_WIDTH = int(CARD_WIDTH * MAT_PERCENT_OVERSIZE)

VERTICAL_MARGIN_PERCENT = 0.20
HORIZONTAL_MARGIN_PERCENT = 0.20

BOTTOM_Y = MAT_HEIGHT / 2 + MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

START_X = MAT_WIDTH / 2 + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

TOP_Y = SCREEN_HEIGHT - MAT_HEIGHT / 2 - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

TOP_X = SCREEN_HEIGHT - MAT_HEIGHT / 2 - MAT_HEIGHT * HORIZONTAL_MARGIN_PERCENT

MIDDLE_Y = TOP_Y - MAT_HEIGHT - MAT_HEIGHT * VERTICAL_MARGIN_PERCENT

MIDDLE_X = SCREEN_WIDTH/2 #- MAT_WIDTH / 2

X_SPACING = MAT_WIDTH + MAT_WIDTH * HORIZONTAL_MARGIN_PERCENT

CARD_VERTICAL_OFFSET = CARD_HEIGHT * CARD_SCALE * 0.3
CARD_HORIZONTAL_OFFSET = CARD_WIDTH * 0.25

PILE_COUNT = 8
HAND = -1
TOP_ROW_PILE_1 = 0
TOP_ROW_PILE_2 = 1
TOP_ROW_PILE_3 = 2
TOP_ROW_PILE_4 = 3
BOTTOM_ROW_PILE_1 = 4
BOTTOM_ROW_PILE_2 = 5
BOTTOM_ROW_PILE_3 = 6
BOTTOM_ROW_PILE_4 = 7

ATACK_ROUND = 1
DEFEND_ROUND = 2

CARD_VALUES = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]
CARD_SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]
FACE_DOWN_IMAGE = f":resources:images/cards/cardBack_red2.png"


class Card(arcade.Sprite):
    def __init__(self, suit, rank, scale=1):
        self.suit = suit
        self.rank = rank
        self.image_file_name = f":resources:images/cards/card{self.suit}{self.rank}.png"

        self.is_face_up = False
        super().__init__(FACE_DOWN_IMAGE, scale, False)

    def face_down(self):
        self.texture = arcade.load_texture(FACE_DOWN_IMAGE)
        self.is_face_up = False

    def face_up(self):
        self.texture = arcade.load_texture(self.image_file_name)
        self.is_face_up = True

    @property
    def is_face_down(self):
        return not self.is_face_up

    def RankIndex(self):
        for rnk in CARD_VALUES:
            if rnk == self.rank:
                return CARD_VALUES.index(rnk)
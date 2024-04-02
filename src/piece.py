import os
from settings import *

class Piece:
    def __init__(self, name, color, value, moved=False, texture=None, texture_rect=None):
        self.name = name
        self.color = color
        self.value = value*VALUE_MULTIPLICATOR
        self.moved = False
        self.moveCounter = 0
        self.texture = texture
        self.set_texture()
        self.texture_rect = texture_rect

    def set_texture(self):
        self.texture = os.path.join(f'assets/{self.color}_{self.name}.png')

class Pawn(Piece):
    def __init__(self, color):
        self.direction = -1 if color == "white" else 1
        super().__init__("pawn", color, 1.0)

class Knight(Piece):
    def __init__(self, color):
        super().__init__('knight', color, 3.0)

class Bishop(Piece):
    def __init__(self, color):
        super().__init__("bishop", color, 3.001)

class Rook(Piece):
    def __init__(self, color):
        super().__init__("rook", color, 5.0)

class Queen(Piece):
    def __init__(self, color):
        super().__init__("queen", color, 9.0)

class King(Piece):
    def __init__(self, color):
        super().__init__("king", color, 1000.0)
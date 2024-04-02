import pygame

from settings import *

class Mouse:
    def __init__(self):
        self.piece = None
        self.dragging = False
        self.promotion = False
        self.mouseX = 0
        self.mouseY = 0
        self.starting_row = 0
        self.starting_col = 0
        self.promotion_row = 0
        self.promotion_col = 0

    def update_blit(self, surface):
        img = pygame.image.load(self.piece.texture)
        img_center = (self.mouseX, self.mouseY)
        self.piece.texture_rect = img.get_rect(center = img_center)
        surface.blit(img, self.piece.texture_rect)

    def update_mouse(self, pos):
        self.mouseX = pos[0]
        self.mouseY = pos[1]

    def save_starting(self, pos):
        self.starting_row = pos[1] // SQ_SIZE
        self.starting_col = pos[0] // SQ_SIZE
        self.starting_row, self.starting_col = self.flip_the_coordinates(self.starting_row, self.starting_col)

    def drag_piece(self, piece):
        if not self.promotion:
            self.piece = piece
            self.dragging = True
    
    def undrag_piece(self):
        self.piece = None
        self.dragging = False

    def start_promotion(self, pos):
        self.dragging = False
        self.promotion = True
        self.promotion_row = pos[1] // SQ_SIZE
        self.promotion_col = pos[0] // SQ_SIZE
        self.promotion_row, self.promotion_col = self.flip_the_coordinates(self.promotion_row, self.promotion_col)

    def end_promotion(self):
        self.piece = None
        self.promotion = False
        self.promotion_row = 0
        self.promotion_col = 0

    def flip_the_coordinates(self, row, col):
        if GAMEMODE == 1:
            row = ROWS - row - 1
            col = COLS - col - 1
        return row, col
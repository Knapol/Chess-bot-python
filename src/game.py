import pygame
from settings import *
from board import Board
from mouse import Mouse
import os

class Game:
    def __init__(self, board: Board, mouse: Mouse):
        self.board = board
        self.mouse = mouse

    def draw_board(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0: 
                    color = (238,238,210)
                else:
                    color = (118,150,86)

                rect = (col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE)

                pygame.draw.rect(surface, color, rect)

    def draw_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    if piece is not self.mouse.piece:
                        real_row, real_col = self.mouse.flip_the_coordinates(row, col)
                        img = pygame.image.load(piece.texture)
                        img_center = ((real_col)*SQ_SIZE + SQ_SIZE // 2, (real_row)*SQ_SIZE + SQ_SIZE // 2)
                        piece.texture_rect = img.get_rect(center = img_center)
                        surface.blit(img, piece.texture_rect)

    def draw_promotion(self, surface, square, piece_color):
        row, col = self.mouse.flip_the_coordinates(square.row, square.col)
        piece_textures = [
            os.path.join(f'assets/{piece_color}_queen.png'),
            os.path.join(f'assets/{piece_color}_knight.png'),
            os.path.join(f'assets/{piece_color}_rook.png'),
            os.path.join(f'assets/{piece_color}_bishop.png')
        ]

        for i in range(4):
            color = (255, 255, 255)
            rect = (col*SQ_SIZE, (row+i)*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(surface, color, rect)

        for i in range(4):
            img = pygame.image.load(piece_textures[i])
            img_center = (col*SQ_SIZE + SQ_SIZE // 2, (row+i)*SQ_SIZE + SQ_SIZE // 2)
            texture_rect = img.get_rect(center = img_center)
            surface.blit(img, texture_rect)

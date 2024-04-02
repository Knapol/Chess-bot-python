import pygame
from sys import exit

from settings import *
from gameManager import GameManager
from move import Move
from square import Square

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")
        self.clock = pygame.time.Clock()
        self.gameManager = GameManager()
        self.board = self.gameManager.board
        self.mouse = self.gameManager.mouse
        self.game = self.gameManager.game
        self.ai = self.gameManager.ai
        self.player_turn = True if (GAMEMODE == 0 and self.board.colour_to_move == "white") or (GAMEMODE == 1 and self.board.colour_to_move == "black") else False

    def is_promotion_square(self, virtual_row, virtual_col):
        piece = self.mouse.piece
        if piece != None and piece.color == self.board.colour_to_move:
            if self.mouse.piece != None and piece.name == "pawn":
                if (piece.color == "white" and virtual_row == 0 and self.mouse.starting_row == 1) or (piece.color == "black" and virtual_row == 7 and self.mouse.starting_row == 6):
                    if (virtual_col == self.mouse.starting_col-1 or virtual_col == self.mouse.starting_col+1):
                        if self.board.squares[virtual_row][virtual_col].has_piece() and self.board.squares[virtual_row][virtual_col].piece.color != piece.color:
                            return True
                    elif virtual_col == self.mouse.starting_col:
                        if not self.board.squares[virtual_row][virtual_col].has_piece():
                            return True
        return False
    
    def mainloop(self):
        while True:
            self.gameManager.moveGenerator.valid_moves = []

            if len(self.board.valid_moves) == 0:
                if self.board.isChecked:
                    if (GAMEMODE == 0 and self.board.moves_log[-1].piece_moved.color == "white") or (GAMEMODE == 1 and self.board.moves_log[-1].piece_moved.color == "black"):
                        print("Human won")
                    else:
                        print("Computer won")
                else:
                    print("Draw")

                pygame.quit()
                exit()

            if not self.player_turn and len(self.board.valid_moves) != 0:
                self.gameManager.move_by_ai()

            self.player_turn = True if (GAMEMODE == 0 and self.board.colour_to_move == "white") or (GAMEMODE == 1 and self.board.colour_to_move == "black") else False

            self.game.draw_board(self.screen)
            self.game.draw_pieces(self.screen)

            if self.mouse.promotion:
                self.game.draw_promotion(self.screen, self.board.squares[self.mouse.promotion_row][self.mouse.promotion_col], self.mouse.piece.color)

            if self.mouse.dragging:
                self.mouse.update_blit(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and self.player_turn: # clicking on a piece
                    self.mouse.update_mouse(event.pos)

                    clicked_row = self.mouse.mouseY // SQ_SIZE
                    clicked_col = self.mouse.mouseX // SQ_SIZE

                    virtual_row, virtual_col = self.mouse.flip_the_coordinates(clicked_row, clicked_col)
                    if not self.mouse.promotion:
                        if self.board.squares[virtual_row][virtual_col].has_piece():
                            self.mouse.save_starting(event.pos)
                            piece = self.board.squares[virtual_row][virtual_col].piece
                            self.mouse.drag_piece(piece)

                elif event.type == pygame.MOUSEMOTION and self.player_turn: # dragging piece over the board
                    if self.mouse.dragging:
                        self.mouse.update_mouse(event.pos)
                        self.game.draw_board(self.screen)
                        self.game.draw_pieces(self.screen)
                        self.mouse.update_blit(self.screen)

                elif event.type == pygame.MOUSEBUTTONUP and self.player_turn: # putting piece on the board
                    self.mouse.update_mouse(event.pos)

                    new_row = self.mouse.mouseY // SQ_SIZE
                    new_col = self.mouse.mouseX // SQ_SIZE

                    virtual_row, virtual_col = self.mouse.flip_the_coordinates(new_row, new_col)
                    starting_square = Square(self.mouse.starting_row, self.mouse.starting_col)
                    ending_square = Square(virtual_row, virtual_col) if not self.mouse.promotion else Square(self.mouse.promotion_row, self.mouse.promotion_col)
                    piece = self.board.squares[virtual_row][virtual_col].piece
                    if self.mouse.promotion:
                        if new_row >= 0 and new_row < 4 and virtual_col == self.mouse.promotion_col:
                            choice = self.board.promotion_squares[new_row]
                            move = Move(starting_square, ending_square, piece, promotion_piece_name=choice)
                            self.gameManager.on_move_chosen(self.mouse.piece, move)
                            
                        self.mouse.end_promotion()

                    elif self.is_promotion_square(virtual_row, virtual_col):
                        self.game.draw_promotion(self.screen, self.board.squares[virtual_row][virtual_col], self.mouse.piece.color)
                        self.mouse.start_promotion(event.pos)
                    else:
                        move = Move(starting_square, ending_square)
                        self.gameManager.on_move_chosen(self.mouse.piece, move)
                        
                        self.mouse.undrag_piece()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:
                        self.gameManager.on_move_unchosen()
                        
                
                elif event.type == pygame.QUIT or len(self.board.valid_moves) == 0:
                    pygame.quit()
                    exit()
            pygame.display.update()
            self.clock.tick(60)

main = Main()
main.mainloop()
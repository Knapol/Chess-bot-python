from settings import *
from piece import *
from random import randint, seed

class Zobrist:
    def __init__(self):
        seed(1000)
        self.zobrist_piece_array = [[[randint(1, 2**64-1) for _ in range(12)] for _ in range(8)] for _ in range(8)]
        self.zobrist_castle_rights_array = [randint(1, 2**64-1) for _ in range(4)] # 0 wq-side, 1 wk-side, 2 bq-side, 3 bk-side
        self.zobrist_enpassant_array = [randint(1, 2**64-1) for _ in range(8)] # 8 is for non enpassant
        self.zobrist_color_to_move = randint(1, 2**64-1)

    def zobrist_hashing(self, board):
        h = 0
        squares = board.sq_with_pieces
        for piece in squares:
            row, col = squares[piece]
            piece_id = self.piece_indexing(piece.name, piece.color)
            h ^= self.zobrist_piece_array[row][col][piece_id]
        
        if board.enPassantSq != ():
            enPassant_id = board.enPassantSq[1]
            h ^= self.zobrist_enpassant_array[enPassant_id]

        for i in range(4):
            if board.castle_rights[i]:
                h ^= self.zobrist_castle_rights_array[i]

        if board.colour_to_move == "black":
            h ^= self.zobrist_color_to_move
            
        return h

    # for each piece type (including both colors) has the id connected to it
    def piece_indexing(self, name, color):
        if name == "pawn" and color == "white":
            return 0
        if name == "knight" and color == "white":
            return 1
        if name == "bishop" and color == "white":
            return 2
        if name == "rook" and color == "white":
            return 3
        if name == "queen" and color == "white":
            return 4
        if name == "king" and color == "white":
            return 5
        if name == "pawn" and color == "black":
            return 6
        if name == "knight" and color == "black":
            return 7
        if name == "bishop" and color == "black":
            return 8
        if name == "rook" and color == "black":
            return 9
        if name == "queen" and color == "black":
            return 10
        if name == "king" and color == "black":
            return 11
        return -1
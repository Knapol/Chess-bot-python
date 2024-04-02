from settings import *
from piece import *
from square import Square

class Fen:
    def __init__(self):
        pass

    def convert_to_board(position, squares, sq_with_pieces):
        #r1bk3r/p2pBpNp/n4n2/1p1NP2P/6P1/3P4/P1P1K3/q5b1 b - - 1 23
        symbols = {
            "p": Pawn,
            "n": Knight,
            "b": Bishop,
            "r": Rook,
            "q": Queen,
            "k": King
        }
        index = 0
        sq = 0
        while position[index] != ' ':
            if position[index] == '/':
                pass
            elif position[index].lower() in symbols:
                color = "black" if position[index].islower() else "white"
                squares[sq//COLS][sq%COLS] = Square(sq//COLS, sq%COLS, symbols[position[index].lower()](color))      

                # having list of squares that have pieces
                sq_with_pieces[squares[sq//COLS][sq%COLS].piece] = (sq//COLS, sq%COLS)
                sq += 1
            else:
                sq += ord(position[index])-48

            index += 1
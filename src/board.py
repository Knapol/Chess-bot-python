from settings import *

from square import Square
from piece import *
from move import Move
from fen import Fen
from zobrist import Zobrist

class Board:
    def __init__(self, zobrist: Zobrist):
        self.squares = [[None for _ in range(COLS)] for _ in range(ROWS)] # virtual represantation of the board
        self.sq_with_pieces = {} # dict stores (row, col) for every piece on board
        self.sq_under_attack = [[False for _ in range(COLS)] for _ in range(ROWS)]
        self.colour_to_move = "white"
        self.valid_moves = [] # stores valid moves for current position
        self.distances = [[] for _ in range(ROWS*COLS)] # for every square on board it stores distances to every border

        self.white_king = None
        self.black_king = None

        self.promotion_squares = ["queen", "knight", "rook", "bishop"]
        self.promotion_classes = {
            "queen": Queen,
            "knight": Knight,
            "rook": Rook,
            "bishop": Bishop
        }

        self.zobrist = zobrist
        self.zobrist_key = None

        # initialize the board - the pieces are put from the fen notation
        self.create_board()
        self.put_pieces("white")
        
        self.white_king_pos = self.get_piece_pos("king", "white")
        self.black_king_pos = self.get_piece_pos("king", "black")

        self.checks = []
        self.pins = []
        self.isChecked = False
        self.isDoubleChecked = False
        self.enPassantSq = () # the square where you can put pawn in order to make en passant move, if there is no such square, then empty tuple
        # self.castle_rights = [True, True, True, True] # 0 wq-side, 1 wk-side, 2 bq-side, 3 bk-side
        self.castle_rights = [False, False, False, False]

        self.moves_log = []
        self.enpassant_log = []

        self.get_distances()

        # self.file = open("Stockfish_help.txt", "a")

    def get_piece_pos(self, name, color):
        for row in range(ROWS):
            for col in range(COLS):
                if self.squares[row][col].has_piece():
                    piece = self.squares[row][col].piece
                    if piece.name == name and piece.color == color:
                        return (row, col)
        return None

    # creates list containing distances for every square to borders from each direction
    def get_distances(self):
        for row in range(ROWS):
            for col in range(COLS):
                north = row
                south = 7 - row
                west = col
                east = 7 - col

                index = COLS*row + col

                self.distances[index] = [
                    north,
                    south,
                    west,
                    east,
                    min(north, east), # north-east -> -7
                    min(south, west), # south-west -> 7
                    min(north, west), # north-west -> -9
                    min(south, east)  # south-east -> 9
                ]

    def get_direction_id(self, direction):
        directions = [-8, 8, -1, 1, -7, 7, -9, 9]
        i = 0
        while directions[i] != direction:
            i+=1
        return i

    def create_board(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def put_pieces(self, color):
        # starting position
        Fen.convert_to_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", self.squares, self.sq_with_pieces)

        # Fen.convert_to_board("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R ", self.squares, self.sq_with_pieces)
        # Fen.convert_to_board("8/k7/3p4/p2P1p2/P2P1P2/8/8/K7 ", self.squares, self.sq_with_pieces)
        # Fen.convert_to_board("3r4/3r4/3k4/8/8/3K4/8/8 w - - 0 1 ", self.squares, self.sq_with_pieces)

        # Fen.convert_to_board("8/1k6/5Q2/6K1/8/8/8/2R5 ", self.squares, self.sq_with_pieces)
        # Fen.convert_to_board("8/1K6/5q2/6k1/8/8/8/2r5 ", self.squares, self.sq_with_pieces)
        # Fen.convert_to_board("3r4/3r4/3k4/8/3K4/8/8/8 ", self.squares, self.sq_with_pieces)
        # Fen.convert_to_board("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8 ", self.squares, self.sq_with_pieces)
        # # Fen.convert_to_board("rnbq1k1r/pp1P1ppp/2p5/2bQ4/2B5/8/PPP1NnPP/RNB2RK1 b - - 0 1 ", self.squares, self.sq_with_pieces)
        # self.colour_to_move = "white"
        # # black king
        # self.squares[0][5].piece.moved = True
        # self.squares[0][5].piece.moveCounter = 1
        # # white pawn
        # self.squares[1][3].piece.moved = True
        # self.squares[1][3].piece.moveCounter = 1

        # self.squares[2][2].piece.moved = True
        # self.squares[2][2].piece.moveCounter = 1

        # # bishop starting
        # self.squares[1][4].piece.moved = True
        # self.squares[1][4].piece.moveCounter = 1
        #bishop moved
        # self.squares[3][2].piece.moved = True 
        # self.squares[3][2].piece.moveCounter = 1 

        # self.squares[6][5].piece.moved = True 
        # self.squares[6][5].piece.moveCounter = 1 

        # self.squares[4][2].piece.moved = True  
        # self.squares[4][2].piece.moveCounter = 1 

        # self.squares[6][4].piece.moved = True
        # self.squares[6][4].piece.moveCounter = 1

        # white queen
        # self.squares[3][3].piece.moved = True
        # self.squares[3][3].piece.moveCounter = 1
        #castle
        # self.squares[7][6].piece.moved = True 
        # self.squares[7][6].piece.moveCounter = 1
        # self.squares[7][5].piece.moved = True   
        # self.squares[7][5].piece.moveCounter = 1 

    def get_notation(self, start_row, start_col, end_row, end_col):
        dict1 = {
            0: "a",
            1: "b",
            2: "c",
            3: "d",
            4: "e",
            5: "f",
            6: "g",
            7: "h"
        }
        dict2 = {
            0: "8",
            1: "7",
            2: "6",
            3: "5",
            4: "4",
            5: "3",
            6: "2",
            7: "1"
        }

        m = f"{dict1[start_col]}{dict2[start_row]}{dict1[end_col]}{dict2[end_row]}"
        return m

    def move(self, piece, move):
        start = move.starting_sq
        end = move.ending_sq
        self.moves_log.append(move)
        self.enpassant_log.append(self.enPassantSq)

        if move.normal_move:
            self.zobrist_key ^= self.zobrist.zobrist_piece_array[start.row][start.col][self.zobrist.piece_indexing(piece.name, piece.color)]
            self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(piece.name, piece.color)]

            if move.piece_captured != None:
                self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(move.piece_captured.name, move.piece_captured.color)]
                self.sq_with_pieces.pop(move.piece_captured)
            self.sq_with_pieces[piece] = (end.row, end.col)

            self.squares[start.row][start.col].piece = None
            self.squares[end.row][end.col].piece = piece

            piece.moved = True
            piece.moveCounter += 1

        elif move.castle_move:
            if end.col == 2:
                self.sq_with_pieces[move.queen_rook] = (end.row, 3)
                self.sq_with_pieces[piece] = (end.row, end.col)

                self.squares[start.row][start.col].piece = None
                self.squares[end.row][end.col].piece = piece
                self.squares[end.row][3].piece = self.squares[end.row][0].piece
                self.squares[end.row][0].piece = None
                piece.moved = True
                piece.moveCounter += 1
                self.squares[end.row][3].piece.moved = True
                self.squares[end.row][3].piece.moveCounter += 1

                self.zobrist_key ^= self.zobrist.zobrist_piece_array[start.row][start.col][self.zobrist.piece_indexing(piece.name, piece.color)]
                self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(piece.name, piece.color)]

                self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][0][self.zobrist.piece_indexing(move.queen_rook.name, piece.color)]
                self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][3][self.zobrist.piece_indexing(move.queen_rook.name, piece.color)]

            else:
                self.sq_with_pieces[move.king_rook] = (end.row, 5)
                self.sq_with_pieces[piece] = (end.row, end.col)

                self.squares[start.row][start.col].piece = None
                self.squares[end.row][end.col].piece = piece
                self.squares[end.row][5].piece = self.squares[end.row][7].piece
                self.squares[end.row][7].piece = None
                piece.moved = True
                piece.moveCounter += 1
                self.squares[end.row][5].piece.moved = True
                self.squares[end.row][5].piece.moveCounter += 1

                self.zobrist_key ^= self.zobrist.zobrist_piece_array[start.row][start.col][self.zobrist.piece_indexing(piece.name, piece.color)]
                self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(piece.name, piece.color)]

                self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][7][self.zobrist.piece_indexing(move.king_rook.name, piece.color)]
                self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][5][self.zobrist.piece_indexing(move.king_rook.name, piece.color)]

        elif move.promotion_move:
            self.zobrist_key ^= self.zobrist.zobrist_piece_array[start.row][start.col][self.zobrist.piece_indexing(piece.name, piece.color)]
            self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(move.promotion_piece.name, piece.color)]

            self.squares[start.row][start.col].piece = None
            self.squares[end.row][end.col].piece = move.promotion_piece

            if move.piece_captured != None:
                self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(move.piece_captured.name, move.piece_captured.color)]
                self.sq_with_pieces.pop(move.piece_captured)
            self.sq_with_pieces.pop(piece)
            self.sq_with_pieces[self.squares[end.row][end.col].piece] = (end.row, end.col)

        elif move.enpassant_move:
            self.zobrist_key ^= self.zobrist.zobrist_piece_array[start.row][start.col][self.zobrist.piece_indexing(piece.name, piece.color)]
            self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(piece.name, piece.color)]

            self.zobrist_key ^= self.zobrist.zobrist_piece_array[start.row][end.col][self.zobrist.piece_indexing(move.piece_captured.name, move.piece_captured.color)]

            self.sq_with_pieces.pop(move.piece_captured)
            self.sq_with_pieces[piece] = (end.row, end.col)
            self.squares[start.row][start.col].piece = None
            self.squares[start.row][end.col].piece = None
            self.squares[end.row][end.col].piece = piece
            piece.moveCounter+=1

        # updating the king position
        if piece.name == "king":
            if piece.color == "white":
                self.white_king_pos = (end.row, end.col)
            else:
                self.black_king_pos = (end.row, end.col)

        # updating en passant square
        # first, removing the last enpassant sq from zobrist hash
        if self.enPassantSq != ():
            self.zobrist_key ^= self.zobrist.zobrist_enpassant_array[self.enPassantSq[1]]

        if piece.name == "pawn" and abs(end.row-start.row) == 2:
            # adding new enpassant sq to zobrist
            self.zobrist_key ^= self.zobrist.zobrist_enpassant_array[start.col]
            self.enPassantSq = (start.row-1, start.col) if piece.color == "white" else (start.row+1, start.col)
        else:
            self.enPassantSq = ()

        self.update_castle_rights() 

        self.colour_to_move = "white" if self.colour_to_move == "black" else "black"
        self.zobrist_key ^= self.zobrist.zobrist_color_to_move
        
    def undo_move(self):
        if len(self.moves_log) > 0:
            move = self.moves_log[-1]
            self.moves_log.pop()
            start = move.starting_sq
            end = move.ending_sq
            if move.normal_move:
                self.zobrist_key ^= self.zobrist.zobrist_piece_array[start.row][start.col][self.zobrist.piece_indexing(move.piece_moved.name, move.piece_moved.color)]
                self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(move.piece_moved.name, move.piece_moved.color)]

                if move.piece_captured != None:
                    self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(move.piece_captured.name, move.piece_captured.color)]
                    self.sq_with_pieces[move.piece_captured] = (end.row, end.col)
                self.sq_with_pieces[move.piece_moved] = (start.row, start.col)
                self.squares[start.row][start.col].piece = move.piece_moved
                self.squares[end.row][end.col].piece = move.piece_captured

                move.piece_moved.moveCounter -= 1
                if move.piece_moved.moveCounter == 0:
                    move.piece_moved.moved = False

            elif move.castle_move:
                if end.col == 2:
                    self.sq_with_pieces[move.queen_rook] = (start.row, 0)
                    self.sq_with_pieces[move.piece_moved] = (start.row, start.col)

                    self.squares[start.row][start.col].piece = move.piece_moved
                    self.squares[end.row][end.col].piece = None
                    self.squares[end.row][3].piece = None
                    self.squares[end.row][0].piece = move.queen_rook
                    move.piece_moved.moved = False
                    move.piece_moved.moveCounter-=1
                    self.squares[end.row][0].piece.moved = False
                    self.squares[end.row][0].piece.moveCounter -= 1

                    self.zobrist_key ^= self.zobrist.zobrist_piece_array[start.row][start.col][self.zobrist.piece_indexing(move.piece_moved.name, move.piece_moved.color)]
                    self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(move.piece_moved.name, move.piece_moved.color)]

                    self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][0][self.zobrist.piece_indexing(move.queen_rook.name, move.piece_moved.color)]
                    self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][3][self.zobrist.piece_indexing(move.queen_rook.name, move.piece_moved.color)]

                else:
                    self.sq_with_pieces[move.king_rook] = (start.row, 7)
                    self.sq_with_pieces[move.piece_moved] = (start.row, start.col)

                    self.squares[start.row][start.col].piece = move.piece_moved
                    self.squares[end.row][end.col].piece = None
                    self.squares[end.row][5].piece = None
                    self.squares[end.row][7].piece = move.king_rook
                    move.piece_moved.moved = False
                    move.piece_moved.moveCounter-=1
                    self.squares[end.row][7].piece.moved = False
                    self.squares[end.row][7].piece.moveCounter -= 1

                    self.zobrist_key ^= self.zobrist.zobrist_piece_array[start.row][start.col][self.zobrist.piece_indexing(move.piece_moved.name, move.piece_moved.color)]
                    self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(move.piece_moved.name, move.piece_moved.color)]

                    self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][7][self.zobrist.piece_indexing(move.king_rook.name, move.piece_moved.color)]
                    self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][5][self.zobrist.piece_indexing(move.king_rook.name, move.piece_moved.color)]

            elif move.promotion_move:
                self.zobrist_key ^= self.zobrist.zobrist_piece_array[start.row][start.col][self.zobrist.piece_indexing(move.piece_moved.name, move.piece_moved.color)]
                self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(move.promotion_piece.name, move.piece_moved.color)]

                if move.piece_captured != None:
                    self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(move.piece_captured.name, move.piece_captured.color)]
                    self.sq_with_pieces[move.piece_captured] = (end.row, end.col)
                self.sq_with_pieces[move.piece_moved] = (start.row, start.col)
                self.sq_with_pieces.pop(move.promotion_piece)

                self.squares[start.row][start.col].piece = move.piece_moved
                self.squares[end.row][end.col].piece = move.piece_captured

            elif move.enpassant_move:
                self.zobrist_key ^= self.zobrist.zobrist_piece_array[start.row][start.col][self.zobrist.piece_indexing(move.piece_moved.name, move.piece_moved.color)]
                self.zobrist_key ^= self.zobrist.zobrist_piece_array[end.row][end.col][self.zobrist.piece_indexing(move.piece_moved.name, move.piece_moved.color)]

                self.zobrist_key ^= self.zobrist.zobrist_piece_array[start.row][end.col][self.zobrist.piece_indexing(move.piece_captured.name, move.piece_captured.color)]

                self.sq_with_pieces[move.piece_captured] = (start.row, end.col)
                self.sq_with_pieces[move.piece_moved] = (start.row, start.col)

                self.squares[start.row][start.col].piece = move.piece_moved
                self.squares[start.row][end.col].piece = move.piece_captured
                self.squares[end.row][end.col].piece = None

                move.piece_moved.moveCounter-=1
                # self.zobrist_key ^= self.zobrist.zobrist_enpassant_array[end.col]
                # self.enPassantSq = (end.row, end.col)

            # removing the current enpassant sq from zobrist hash
            if self.enPassantSq != ():
                self.zobrist_key ^= self.zobrist.zobrist_enpassant_array[self.enPassantSq[1]]

            new_enPassantSq = self.enpassant_log[-1]
            self.enpassant_log.pop()
            # adding new enpassant sq to zobrist hash
            if new_enPassantSq != ():
                self.zobrist_key ^= self.zobrist.zobrist_enpassant_array[new_enPassantSq[1]]
            self.enPassantSq = new_enPassantSq
            
            if move.piece_moved.name == "king":
                if move.piece_moved.color == "white":
                    self.white_king_pos = (start.row, start.col)
                else:
                    self.black_king_pos = (start.row, start.col)

            # updating castle rights
            self.update_castle_rights()

            self.colour_to_move = "white" if self.colour_to_move == "black" else "black"
            self.zobrist_key ^= self.zobrist.zobrist_color_to_move

    def update_castle_rights(self):
        new_castle_rights = [False, False, False, False]

        # first for white
        left_rook = self.squares[7][0]
        right_rook = self.squares[7][7]
        king = self.squares[7][4]

        if king.has_piece() and king.piece.name == "king" and king.piece.color == "white":
            if king.piece.moveCounter == 0:
                if left_rook.has_piece() and left_rook.piece.name == "rook" and left_rook.piece.color == "white":
                    if left_rook.piece.moveCounter == 0:
                        new_castle_rights[0] = True
                            
                if right_rook.has_piece() and right_rook.piece.name == "rook" and right_rook.piece.color == "white":
                    if right_rook.piece.moveCounter == 0:
                        new_castle_rights[1] = True
        
        # now, the black rights
        left_rook = self.squares[0][0]
        right_rook = self.squares[0][7]
        king = self.squares[0][4]
        
        if king.has_piece() and king.piece.name == "king" and king.piece.color == "black":
            if king.piece.moveCounter == 0:
                if left_rook.has_piece() and left_rook.piece.name == "rook" and left_rook.piece.color == "black":
                    if left_rook.piece.moveCounter == 0:
                        new_castle_rights[2] = True
                            
                if right_rook.has_piece() and right_rook.piece.name == "rook" and right_rook.piece.color == "black":
                    if right_rook.piece.moveCounter == 0:
                        new_castle_rights[3] = True

        for i in range(4):
            if new_castle_rights[i] != self.castle_rights[i]:
                self.castle_rights[i] = new_castle_rights[i]
                self.zobrist_key ^= self.zobrist.zobrist_castle_rights_array[i]

    # function testing moves generator
    def simulate_game(self, depth, pos_counter, max_depth, pos_checks, pos_check_mates, pos_captures, pos_enp, pos_normal_moves):
        pos_counter[depth]+=len(self.valid_moves)
        pos_checks[depth]+=len(self.checks)
        if len(self.valid_moves) == 0:
            pos_check_mates[depth]+=1

        if depth == max_depth:
            for m in self.valid_moves:
                if m.piece_captured != None:
                    pos_captures[depth]+=1
                else:
                    if m.normal_move:
                        pos_normal_moves[depth]+=1
                if m.enpassant_move:
                    pos_enp[depth]+=1
            return
          
        vaildMoves = self.valid_moves
        checks = self.checks
        pins = self.pins
        isChecked = self.isChecked
        isDoubleChecked = self.isDoubleChecked
        enPassantSq = self.enPassantSq

        for move in vaildMoves:
            self.move(move.piece_moved, move)
            if move.piece_captured != None:
                pos_captures[depth]+=1
            else:
                if move.normal_move:
                    pos_normal_moves[depth]+=1
            if move.enpassant_move:
                pos_enp[depth]+=1

            # if depth == 0:
            #     self.file.write(f"{self.get_notation(move.starting_sq.row, move.starting_sq.col, move.ending_sq.row, move.ending_sq.col)}   ")

            self.simulate_game(depth+1, pos_counter, max_depth, pos_checks, pos_check_mates, pos_captures, pos_enp, pos_normal_moves)
            
            # if depth == 0:
            #     self.file.write(f"{pos_counter[max_depth]}\n")
            #     pos_counter[max_depth]=0
            
            self.undo_move()
            self.valid_moves = vaildMoves
            self.checks = checks
            self.pins = pins
            self.isChecked = isChecked
            self.isDoubleChecked = isDoubleChecked
            self.enPassantSq = enPassantSq

        # if depth == 0:
        #     self.file.close()
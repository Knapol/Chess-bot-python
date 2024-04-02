from settings import *

from square import Square
from piece import *
from move import Move

from board import Board

class MoveGenerator:
    def __init__(self, board: Board):
        self.board = board
        self.valid_moves = []

    def search_for_check_and_pins(self, piece, s_row, s_col):
        pins = []
        checks = []

        #searching for queen, rook, and bishop checks and pins
        directions = [-8, 8, -1, 1, -7, 7, -9, 9]
        # to optimize, because for example if you dont have queen, and rook, than there is no need for testing straight lines
        start_index = 0
        end_index = 8
        
        for direction_index in range(start_index, end_index):
            possible_pin = ()
            for i in range(self.board.distances[s_row*COLS+s_col][direction_index]):
                is_diagonal = False if direction_index < 4 else True
                index = s_row*COLS + s_col + (i+1) * directions[direction_index]
                row = index // COLS
                col = index % COLS
                sq = self.board.squares[row][col]
                if sq.has_piece():
                    if sq.piece.color == piece.color:
                        if possible_pin != (): 
                            # we found another piece of the same color so there is no pin
                            break
                        else:
                            # the piece is potentially pinned
                            possible_pin = (row, col, directions[direction_index])
                    else:
                        if sq.is_type_correct(is_diagonal):
                            if possible_pin == ():
                                # the king is in check
                                checks.append((row, col, directions[direction_index], sq.piece.name))
                                break
                            else:
                                # the piece is pinned
                                pins.append(possible_pin)
                        else:
                            # there is a piece of the oppposite color, but this piece is not dangerous
                            break

        # searching for knight checks
        knight_moves = [
            (-1, -2),
            (-2,-1),
            (-2, 1),
            (-1, 2),
            (1, 2),
            (2, 1),
            (2, -1),
            (1, -2)
        ]
        
        for x, y in knight_moves:
            row = s_row + x
            col = s_col + y
            if row >= 0 and row < ROWS and col >= 0 and col < COLS:
                sq = self.board.squares[row][col]
                if sq.has_piece() and sq.piece.color != piece.color and sq.piece.name == "knight":
                    checks.append((row, col, (x, y), "knight"))
        
        # searching for pawn checks
        pawns_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        p_start = 0 if piece.color == "white" else 2
        p_end = 2 if piece.color == "white" else 4

        for i in range(p_start, p_end):
            row = s_row+pawns_directions[i][0]
            col = s_col+pawns_directions[i][1]
            if row >= 0 and row < ROWS and col >= 0 and col < COLS:
                sq = self.board.squares[row][col]
                if sq.has_piece() and sq.piece.color != piece.color and sq.piece.name == "pawn":
                    checks.append((row, col, pawns_directions[i], "pawn"))

        # searching if opposite king is nearby
        # in order to search for king I just use the list of directions from queen and etc
        for direction_index in range(8):
            if self.board.distances[s_row*COLS+s_col][direction_index] > 0:
                index = s_row*COLS+s_col + directions[direction_index]
                row = index // COLS
                col = index % COLS
                sq = self.board.squares[row][col]
                if sq.has_piece() and sq.piece.name == "king":
                    checks.append((row, col, (row, col), "king"))

        in_check = False if len(checks) == 0 else True
        in_double_check = True if len(checks) >= 2 else False
        return in_check, in_double_check, checks, pins

    def generate_moves(self):
        self.valid_moves = []
        if self.board.colour_to_move == "white":
            kingPos = self.board.white_king_pos
        else:
            kingPos = self.board.black_king_pos

        isChecked, isDoubleCheck, checks, pins = self.search_for_check_and_pins(self.board.squares[kingPos[0]][kingPos[1]].piece, kingPos[0], kingPos[1])
        self.board.isChecked = isChecked
        self.board.isDoubleChecked = isDoubleCheck
        self.board.checks = checks
        self.board.pins = pins

        for piece in self.board.sq_with_pieces:
            row, col = self.board.sq_with_pieces[piece] 
            if piece.color == self.board.colour_to_move:
                if piece.name == "pawn" and not isDoubleCheck:
                    self.get_pawn_moves(piece, row, col)
                if (piece.name == "bishop" or piece.name == "rook" or piece.name == "queen") and not isDoubleCheck:
                    self.get_slide_moves(piece, row, col)
                if piece.name == "knight" and not isDoubleCheck:
                    self.get_knight_moves(piece, row ,col)
                if piece.name == "king":
                    self.get_king_moves(piece, row, col)
        
        if isChecked and not isDoubleCheck:
            tmp_valid_moves = []
            valid_squares = []
            s_row, s_col = self.board.checks[0][0], self.board.checks[0][1]
            if self.board.checks[0][3] == "knight" or self.board.checks[0][3] == "pawn":
                valid_squares.append((s_row, s_col))
            else:
                valid_squares.append((s_row, s_col))
                direction = -self.board.checks[0][2]
                direction_id = self.board.get_direction_id(direction)
                for i in range(self.board.distances[s_row*COLS+s_col][direction_id]):
                    index = s_row*COLS+s_col + (i+1) * direction
                    row = index // COLS
                    col = index % COLS
                    if row == kingPos[0] and col == kingPos[1]:
                        break
                    valid_squares.append((row, col))

            for move in self.valid_moves:
                s_row, s_col = move.starting_sq.row, move.starting_sq.col
                row, col = move.ending_sq.row, move.ending_sq.col
                if self.board.squares[s_row][s_col].piece.name != "king":
                    for sq in valid_squares:
                        if sq[0] == row and sq[1] == col:
                            tmp_valid_moves.append(move)
                            break
                else:
                    tmp_valid_moves.append(move)
        
            self.valid_moves = tmp_valid_moves
        return self.valid_moves

    def create_promotion_moves(self, piece, row, col, new_row, new_col, captured):
        for i in range(4):
            new_move = Move(Square(row, col), Square(new_row, new_col), piece, captured, self.board.promotion_squares[i])
            new_move.promotion_piece = self.board.promotion_classes[new_move.promotion_piece_name](piece.color)
            self.valid_moves.append(new_move)

    # functions helps in checking if en passant is legal
    def search_left(self, row, col):
        for new_col in range(col-1, -1, -1):
            if self.board.squares[row][new_col].has_piece():
                return self.board.squares[row][new_col].piece
        return None

    def search_right(self, row, col):
        for new_col in range(col+1, COLS):
            if self.board.squares[row][new_col].has_piece():
                return self.board.squares[row][new_col].piece
        return None

    def get_pawn_moves(self, piece, row, col):
        # checking if pawn can move forward (also inlcudes moving two squares forward)
        step = 2 if ((row == 6 and piece.color == "white") or (row == 1 and piece.color == "black")) else 1
        # step = 1 if piece.moved else 2
        start_row = row + piece.direction
        end_row =  row + (1 + step) * piece.direction
        isPinned = False
        pinDirection = None

        #testing if pawn is pinned
        for i in range(len(self.board.pins)-1, -1, -1):
            if self.board.pins[i][0] == row and self.board.pins[i][1] == col:
                isPinned = True
                pinDirection = self.board.pins[i][2]
                break

        if isPinned and self.board.isChecked:
            return

        for new_row in range(start_row, end_row, piece.direction):
            if (not isPinned or pinDirection == -8 or pinDirection == 8) and new_row >= 0 and new_row < ROWS and not self.board.squares[new_row][col].has_piece():
                if new_row == 0 or new_row == 7:
                    self.create_promotion_moves(piece, row, col, new_row, col, None)
                else:
                    new_move = Move(Square(row, col), Square(new_row, col), piece)
                    self.valid_moves.append(new_move)
            else:
                break

        # checking if pawn can take piece from right
        new_row = row + piece.direction
        if col+1 >= 0 and col+1 < COLS:
            if not isPinned or (pinDirection == -7 and piece.color == "white") or (pinDirection == 9 and piece.color == "black"):
                sq = self.board.squares[new_row][col+1]
                if sq.has_piece() and sq.piece.color != piece.color:
                    if new_row == 0 or new_row == 7:
                        self.create_promotion_moves(piece, row, col, new_row, col+1, self.board.squares[new_row][col+1].piece)
                    else:
                        new_move = Move(Square(row, col), Square(new_row, col+1), piece, self.board.squares[new_row][col+1].piece)
                        self.valid_moves.append(new_move)
                elif (new_row, col+1) == self.board.enPassantSq:
                    p1 = self.search_left(row, col)
                    p2 = self.search_right(row, col+1)
                    enp = True
                    if p1 != None and p2 != None:
                        if (p1.color == piece.color and p1.name == "king") or (p2.color == piece.color and p2.name == "king"):
                            if (p1.color != piece.color and (p1.name == "rook" or p1.name == "queen")) or (p2.color != piece.color and (p2.name == "rook" or p2.name == "queen")):
                                enp = False
                    if enp:
                        new_move = Move(Square(row, col), Square(new_row, col+1), piece, self.board.squares[row][col+1].piece, enpassant_move=True)
                        self.valid_moves.append(new_move)

        # checking if pawn can take piece from left
        if col-1 >= 0 and col-1 < COLS:
            if not isPinned or (pinDirection == -9 and piece.color == "white") or (pinDirection == 7 and piece.color == "black"):
                sq = self.board.squares[new_row][col-1]
                if sq.has_piece() and sq.piece.color != piece.color:
                    if new_row == 0 or new_row == 7:
                        self.create_promotion_moves(piece, row, col, new_row, col-1, self.board.squares[new_row][col-1].piece)
                    else:
                        new_move = Move(Square(row, col), Square(new_row, col-1), piece, self.board.squares[new_row][col-1].piece)
                        self.valid_moves.append(new_move)
                elif (new_row, col-1) == self.board.enPassantSq:
                    p1 = self.search_left(row, col-1)
                    p2 = self.search_right(row, col)
                    enp = True
                    if p1 != None and p2 != None:
                        if (p1.color == piece.color and p1.name == "king") or (p2.color == piece.color and p2.name == "king"):
                            if (p1.color != piece.color and (p1.name == "rook" or p1.name == "queen")) or (p2.color != piece.color and (p2.name == "rook" or p2.name == "queen")):
                                enp = False
                    if enp:
                        new_move = Move(Square(row, col), Square(new_row, col-1), piece, self.board.squares[row][col-1].piece, enpassant_move=True)
                        self.valid_moves.append(new_move)

    # slide moves are moves made by queen, rook, and bishop
    def get_slide_moves(self, piece, s_row, s_col):
        directions = [-8, 8, -1, 1, -7, 7, -9, 9]
        start_index = 4 if piece.name == "bishop" else 0
        end_index = 4 if piece.name == "rook" else 8
        isPinned = False
        pinDirection = None

        for i in range(len(self.board.pins)-1, -1, -1):
            if s_row == self.board.pins[i][0] and s_col == self.board.pins[i][1]:
                isPinned = True
                pinDirection = self.board.pins[i][2]
                break

        if isPinned and self.board.isChecked:
            return

        for direction_index in range(start_index, end_index):
            if not isPinned or ( directions[direction_index] == pinDirection or directions[direction_index] == -pinDirection):

                for i in range(self.board.distances[s_row*COLS+s_col][direction_index]):
                    index = s_row*COLS+s_col + (i+1) * directions[direction_index]
                    row = index // COLS
                    col = index % COLS

                    # if moving piece has the same color as piece on the square, it can't go further
                    if self.board.squares[row][col].has_piece() and self.board.squares[row][col].piece.color == piece.color: 
                        break
                    
                    new_move = Move(Square(s_row, s_col), Square(row, col), piece, self.board.squares[row][col].piece)
                    self.valid_moves.append(new_move)

                    # if the piece on the square was taken, we can't go further
                    if self.board.squares[row][col].has_piece() and self.board.squares[row][col].piece.color != piece.color: 
                        break
    
    def get_knight_moves(self, piece, s_row, s_col):
        knight_moves = [
            (-1, -2),
            (-2,-1),
            (-2, 1),
            (-1, 2),
            (1, 2),
            (2, 1),
            (2, -1),
            (1, -2)
        ]

        for i in range(len(self.board.pins)-1, -1, -1):
            if s_row == self.board.pins[i][0] and s_col == self.board.pins[i][1]:
                return

        for x, y in knight_moves:
            row = s_row + x
            col = s_col + y
            if row >= 0 and row < ROWS and col >= 0 and col < COLS:
                if not self.board.squares[row][col].has_piece() or ( self.board.squares[row][col].has_piece() and self.board.squares[row][col].piece.color != piece.color ):
                    new_move = Move(Square(s_row, s_col), Square(row, col), piece, self.board.squares[row][col].piece)
                    self.valid_moves.append(new_move)

    def get_king_moves(self, piece, s_row, s_col):
        directions = [-8, 8, -1, 1, -7, 7, -9, 9]
        # normal moves (even if king is in check/will be/will go near the opposite king)
        for direction_index in range(8):
            if self.board.distances[s_row*COLS+s_col][direction_index] > 0:
                index = s_row*COLS+s_col + directions[direction_index]
                row = index // COLS
                col = index % COLS
                
                if not self.board.squares[row][col].has_piece() or ( self.board.squares[row][col].has_piece() and self.board.squares[row][col].piece.color != piece.color ):
                    tmp_piece = self.board.squares[row][col].piece
                    self.board.squares[row][col].piece = piece
                    self.board.squares[s_row][s_col].piece = None
                    isChecked, isDoubleCheck, checks, pins = self.search_for_check_and_pins(piece, row, col)
                    if not isChecked:
                        new_move = Move(Square(s_row, s_col), Square(row, col), piece, tmp_piece)
                        self.valid_moves.append(new_move)
                    self.board.squares[s_row][s_col].piece = piece
                    self.board.squares[row][col].piece = tmp_piece
        
        # castle
        if not piece.moved:
            left_space = 3
            right_space = 6

            # queen side
            if self.board.squares[s_row][0].has_piece():
                left_rook = self.board.squares[s_row][0].piece
                if left_rook.name == "rook" and left_rook.color == piece.color and not left_rook.moved:
                    is_freespace = True
                    for i in range(1, left_space+1):
                        if self.board.squares[s_row][i].has_piece():
                            is_freespace = False
                            break
                    if is_freespace:
                        # theoretically i will searching if ending square is in check two times, so maybe i shouldnt xD
                        if not self.board.isChecked and self.is_square_in_check(s_row, 2, piece) and self.is_square_in_check(s_row, 3, piece):
                            new_move = Move(Square(s_row, s_col), Square(s_row, 2), piece, castle_move=True)
                            new_move.castle_move = True
                            new_move.queen_rook = left_rook
                            self.valid_moves.append(new_move)
            
            # king side
            if self.board.squares[s_row][7].has_piece():
                right_rook = self.board.squares[s_row][7].piece
                if right_rook.name == "rook" and right_rook.color == piece.color and not right_rook.moved:
                    is_freespace = True
                    for i in range(5, right_space+1):
                        if self.board.squares[s_row][i].has_piece():
                            is_freespace = False
                            break
                    if is_freespace:
                        if not self.board.isChecked and self.is_square_in_check(s_row, 5, piece) and self.is_square_in_check(s_row, 6, piece):
                            new_move = Move(Square(s_row, s_col), Square(s_row, 6), piece, castle_move=True)
                            new_move.king_rook = right_rook
                            self.valid_moves.append(new_move)
        
    def is_square_in_check(self, row, col, piece):
        if piece.color == "white":
            kingPos = self.board.white_king_pos
        else:
            kingPos = self.board.black_king_pos

        s_row, s_col = kingPos
        self.board.squares[row][col].piece = piece
        self.board.squares[s_row][s_col].piece = None
        isChecked, isDoubleCheck, checks, pins = self.search_for_check_and_pins(piece, row, col)

        self.board.squares[row][col].piece = None
        self.board.squares[s_row][s_col].piece = piece

        if isChecked:
            return False
        return True
    
    
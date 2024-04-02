class Move:
    def __init__(self, starting_sq, ending_sq, piece_moved=None, piece_captured=None, promotion_piece_name=None, enpassant_move=False, castle_move=False):
        self.starting_sq = starting_sq
        self.ending_sq = ending_sq

        self.piece_moved = piece_moved
        self.piece_captured = piece_captured

        # promotion variables
        self.promotion_move = piece_moved != None and piece_moved.name == "pawn" and ((ending_sq.row == 0 and piece_moved.color == "white") or (ending_sq.row == 7 and piece_moved.color == "black"))
        self.promotion_piece_name = promotion_piece_name
        self.promotion_piece = None

        # en passant variables
        self.enpassant_move = enpassant_move

        # castle variables
        self.castle_move = castle_move
        self.queen_rook = None
        self.king_rook = None

        self.normal_move = not self.promotion_move and not self.castle_move and not self.enpassant_move

    def __eq__(self, other):
        return self.starting_sq == other.starting_sq and self.ending_sq == other.ending_sq and self.promotion_piece_name == other.promotion_piece_name
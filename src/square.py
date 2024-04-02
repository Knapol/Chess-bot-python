class Square:
    def __init__(self, row, col, piece=None):
        self.row = row
        self.col = col
        self.piece = piece

    def has_piece(self):
        if self.piece == None:
            return False
        return True
    
    def is_type_correct(self, is_diagonal):
        piece = self.piece
        if ( is_diagonal and (piece.name == "queen" or piece.name == "bishop") ) or ( not is_diagonal and (piece.name == "queen" or piece.name == "rook") ):
            return True
        return False
    
    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
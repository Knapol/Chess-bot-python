from settings import *

from square import Square
from piece import *
from move import Move
from board import Board

from math import inf

from moveGenerator import MoveGenerator
from pieceSquaresTables import *
from transpositionTables import TranspositionTable

class Ai:
    def __init__(self, moveGenerator: MoveGenerator):
        self.size = 64000
        self.moveGenerator = moveGenerator
        self.transpositionTable = TranspositionTable(self.size)
        self.t_counter = 0
        self.node_counter = 0
        self.best_previous_move = None

    def get_move(self, moves, board):
        depth = 3
        self.t_counter = 0
        self.node_counter = 0
        return self.search(moves, board, depth, depth, -inf, inf)

    def search(self, moves, board: Board, depth, max_depth, alpha, beta):
        bestMoveInPosition = None
        
        tt_val = self.transpositionTable.investigate_evaluation(board.zobrist_key, alpha, beta, depth)
        
        if tt_val is not None:
            self.t_counter += 1
            if depth == max_depth:
                return self.transpositionTable.get_stored_move(board.zobrist_key)
            return tt_val
        
        if len(moves) == 0:
            if board.isChecked:
                return -inf
            return 0
        
        if depth == 0:
            self.node_counter += 1
            return -self.evaluate(board)
        
        checks = board.checks
        pins = board.pins
        isChecked = board.isChecked
        isDoubleChecked = board.isDoubleChecked
        enPassantSq = board.enPassantSq

        validMoves = moves
        validMoves = self.move_ordering(validMoves)

        eval_type = "UpperBound"

        for i in range(len(validMoves)):
            index = validMoves[i][1]
            board.move(moves[index].piece_moved, moves[index])

            nextMoves = self.moveGenerator.generate_moves()

            evaluation_score = -self.search(nextMoves, board, depth-1, max_depth, -beta, -alpha)
            board.undo_move()
            board.checks = checks
            board.pins = pins
            board.isChecked = isChecked
            board.isDoubleChecked = isDoubleChecked
            board.enPassantSq = enPassantSq

            if evaluation_score >= beta:
                self.transpositionTable.add_evalution(board.zobrist_key, beta, depth, "LowerBound", moves[index])
                if depth == max_depth:
                    return moves[index]
                else:
                    return beta
                
            if evaluation_score > alpha:
                eval_type = "Exact"
                alpha = evaluation_score
                bestMoveInPosition = moves[index]

        self.transpositionTable.add_evalution(board.zobrist_key, alpha, depth, eval_type, bestMoveInPosition)

        if depth == max_depth:
            if alpha == -inf:
                return moves[0]
            else:
                print(alpha)
                return bestMoveInPosition
        else:
            return alpha

    # based only on material
    def evaluate(self, board: Board):
        evaluation = 0

        evaluation += self.count_material(board)

        evaluation += self.evaluate_piece_square_tables(board)

        return evaluation

    def count_material(self, board: Board):
        material = 0
        for piece in board.sq_with_pieces:
            if piece.color != board.colour_to_move:
                material += piece.value
            else:
                material -= piece.value
        return material

    def move_ordering(self, moves):
        rated_moves = []
        for i in range(len(moves)):
            move = moves[i]
            guess_score = 0

            if move.piece_captured != None:
                guess_score = 10*move.piece_captured.value - move.piece_moved.value

            if move.promotion_move:
                guess_score += move.promotion_piece.value

            if self.best_previous_move is not None:
                if move == self.best_previous_move:
                    guess_score += 10000

            rated_moves.append((guess_score, i))

        rated_moves.sort(key=lambda x: x[0], reverse=True)
        return rated_moves
    
    def evaluate_piece_square_tables(self, board: Board):
        value = 0
        for piece in board.sq_with_pieces:
            row, col = board.sq_with_pieces[piece]
            if piece.color != board.colour_to_move:
                if piece.name == "pawn":
                    value += read(pawns, row, col, piece.color)

                if piece.name == "knight":
                    value += read(knights, row, col, piece.color)

                if piece.name == "bishop":
                    value += read(bishops, row, col, piece.color)

                if piece.name == "rook":
                    value += read(rooks, row, col, piece.color)

                if piece.name == "queen":
                    value += read(queens, row, col, piece.color)

                if piece.name == "king":
                    value += read(kingEndGame, row, col, piece.color)
            else:
                if piece.name == "pawn":
                    value -= read(pawns, row, col, piece.color)

                if piece.name == "knight":
                    value -= read(knights, row, col, piece.color)

                if piece.name == "bishop":
                    value -= read(bishops, row, col, piece.color)

                if piece.name == "rook":
                    value -= read(rooks, row, col, piece.color)

                if piece.name == "queen":
                    value -= read(queens, row, col, piece.color)

                if piece.name == "king":
                    value -= read(kingEndGame, row, col, piece.color)

        return value
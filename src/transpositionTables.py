from settings import *

from square import Square
from piece import *
from board import Board

class TranspositionTable:
    def __init__(self, size):
        self.size = size
        self.positions = [Position() for _ in range(size)]
        self.exact_cnt = 0
        self.upper_cnt = 0
        self.lower_cnt = 0
        
    # check if we searched this position and if we can use its evaluation in current search
    def investigate_evaluation(self, key, alpha, beta, depth):
        pos = self.positions[key % self.size]

        if pos.key == key:
            if pos.depth >= depth:
                if pos.node_type == "Exact":
                    self.exact_cnt += 1
                    return pos.score
                
                if pos.node_type == "UpperBound" and pos.score <= alpha:
                    self.upper_cnt += 1
                    return pos.score
                
                if pos.node_type == "LowerBound" and pos.score >= beta:
                    self.lower_cnt += 1
                    return pos.score

        return None

    def add_evalution(self, key, value, depth, node_type, move):
        index = key % self.size
        self.positions[index].key = key
        self.positions[index].score = value
        self.positions[index].depth = depth
        self.positions[index].node_type = node_type
        self.positions[index].move = move

    def get_stored_move(self, key):
        return self.positions[key % self.size].move

    def clear(self):
        self.positions = [Position() for _ in range(self.size)]


class Position:
    def __init__(self, key=None, score=None, depth=None, node_type=None, move = None):
        self.key = key
        self.score = score
        self.depth = depth
        self.node_type = node_type
        self.move = move
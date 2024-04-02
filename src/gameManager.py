from settings import *
from board import Board
from mouse import Mouse
from game import Game
from moveGenerator import MoveGenerator
from ai import Ai
from zobrist import Zobrist

import datetime

class GameManager:
    def __init__(self):
        self.zobrist = Zobrist()
        self.board = Board(self.zobrist)
        self.mouse = Mouse()
        self.game = Game(self.board, self.mouse)
        self.moveGenerator = MoveGenerator(self.board)
        self.ai = Ai(self.moveGenerator)
        
        self.board.zobrist_key = self.zobrist.zobrist_hashing(self.board)
        
        self.board.valid_moves = self.moveGenerator.generate_moves()

    def on_move_chosen(self, piece, move):
        for m in self.board.valid_moves:
            if move == m:
                move = m
                self.board.move(piece, move)
                self.board.valid_moves = []
                self.board.valid_moves = self.moveGenerator.generate_moves()

    def on_move_unchosen(self):
        self.board.undo_move()
        self.board.valid_moves = []
        self.board.valid_moves = self.moveGenerator.generate_moves()

    def move_by_ai(self):
        m = self.ai.get_move(self.board.valid_moves, self.board)
        self.board.move(m.piece_moved, m)
        self.board.valid_moves = []
        self.board.valid_moves = self.moveGenerator.generate_moves()

    def perftest(self):
        a = datetime.datetime.now()
        max_depth = 4
        pos_counter = [0 for _ in range(max_depth+1)]
        pos_checks = [0 for _ in range(max_depth+1)]
        pos_check_mates = [0 for _ in range(max_depth+1)]
        pos_captures = [0 for _ in range(max_depth+1)]
        pos_enp = [0 for _ in range(max_depth+1)]
        pos_normal_moves = [0 for _ in range(max_depth+1)] # the moves without captures, and not the special ones
        self.board.simulate_game(0, pos_counter, max_depth, pos_checks, pos_check_mates, pos_captures, pos_enp, pos_normal_moves)
        b = datetime.datetime.now()
        delta = b - a
        print(int(delta.total_seconds() * 1000))

        for i in range(max_depth+1):
            print("depth: ", i+1, "moves: ", pos_counter[i])

        for i in range(max_depth+1):
            print("depth: ", i+1, "checks: ", pos_checks[i])

        for i in range(max_depth+1):
            print("depth: ", i+1, "check mates: ", pos_check_mates[i])
        
        for i in range(max_depth+1):
            print("depth: ", i+1, "captures: ", pos_captures[i])

        for i in range(max_depth+1):
            print("depth: ", i+1, "enp: ", pos_enp[i])

        for i in range(max_depth+1):
            print("depth: ", i+1, "normal without capture: ", pos_normal_moves[i])
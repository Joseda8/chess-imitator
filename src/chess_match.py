import random

import chess

from chess_student import ChessStudent
from logger import setup_logging


# Set up the logging configuration
logger = setup_logging()


class ChessMatch:
    def __init__(self, chess_student: ChessStudent):
        """
        Initializes the ChessMatch instance.

        :param chess_student: An instance of the ChessStudent class.
        :type chess_student: ChessStudent
        """
        self.chess_student = chess_student

    def make_move(self, board):
        """
        Generates a move for the bot based on the k-NN classifier.
        
        :param board: The current chess board.
        :type board: chess.Board
        :return: The generated move.
        :rtype: chess.Move
        """
        fen = board.board_fen()
        fen = self.chess_student.fen_to_encoded_list(fen)
        move_indices = self.chess_student.clf.predict([fen])[0]
        move = self.chess_student.move_to_uci(move_indices)
        move = chess.Move.from_uci(move)

        if move not in board.legal_moves:
            logger.warning("A random move was made instead of a predicted one.")
            move = random.choice(list(board.legal_moves))
        return move

    def play_game(self):
        """
        Plays a game of chess against the human player.
        """
        board = chess.Board()
        while not board.is_game_over():
            if board.turn == chess.WHITE:
                move = input('Enter your move: ')
                board.push_uci(move)
            else:
                move = self.make_move(board)
                print(f"Bot's move: {move.uci()}")
                board.push(move)

        print(board.result())

# Usage
chess_student = ChessStudent(games_directory="matches", player_name="Hikaru")
chess_match = ChessMatch(chess_student)
chess_match.play_game()

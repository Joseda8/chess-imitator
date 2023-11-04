import argparse
import random

import chess

from chess_student import ChessStudent
from logger import setup_logging


# Set up the logging configuration
logger = setup_logging()

class ChessMatch:
    def __init__(self, chess_student: ChessStudent, bot_color: chess.Color):
        """
        Initializes the ChessMatch instance.
        :param chess_student: An instance of the ChessStudent class.
        :type chess_student: ChessStudent
        :param bot_color: The color that the bot is playing as.
        :type bot_color: chess.Color
        """
        self.chess_student = chess_student
        self.bot_color = bot_color

    def move_to_uci(self, move_indices):
        """
        Converts a list of move indices to a UCI move string.
        :param move_indices: The list of move indices to convert.
        :type move_indices: list
        :return: The UCI move string.
        :rtype: str
        """
        start_square = chess.square_name(move_indices[0])
        target_square = chess.square_name(move_indices[1])
        return start_square + target_square

    def make_move(self, board):
        """
        Generates a move for the bot based on the k-NN classifier.
        :param board: The current chess board.
        :type board: chess.Board
        :return: The generated move.
        :rtype: chess.Move
        """
        fen = board.board_fen()
        fen = self.chess_student.fen_to_encoded_list(fen.replace("/", "").replace(" ", ""))
        move_indices = self.chess_student.bot.predict([fen])[0]
        move = self.move_to_uci(move_indices)
        move = chess.Move.from_uci(move)

        if move not in board.legal_moves:
            logger.warning(f"A random move was made instead of a predicted one. Predicted move was: {move}")
            move = random.choice(list(board.legal_moves))
        return move

    def play_game(self):
        """
        Plays a game of chess against the human player.
        """
        board = chess.Board()
        while not board.is_game_over():
            if board.turn == self.bot_color:
                move = self.make_move(board)
                logger.info(f"Bot's move: {move.uci()}")
                board.push(move)
            else:
                move = input("Enter your move: ")
                board.push_uci(move)

            # Flip the board if the bot is playing as black
            if self.bot_color == chess.BLACK:
                print(f"Board state:\n{board.transform(chess.flip_vertical)}")
            else:
                print(f"Board state:\n{board}")
        logger.info(board.result())


# -----------------
# Main
# -----------------

# Set up argument parser
parser = argparse.ArgumentParser(description="Play a game of chess against a trained bot.")
parser.add_argument("--games_directory", type=str, help="The directory where the PGN games files are stored.")
parser.add_argument("--player_name", type=str, help="The name of the player that the bot should learn moves from.")
parser.add_argument("--cache", action="store_true", help="Indicates whether the results should be cached.")
parser.add_argument("--bot_color", type=str, choices=["white", "black"], default="white", help="The color that the bot is playing as (white or black).")
parser.add_argument("--algorithm", type=str, choices=["knn", "rf"], default="knn", help="The machine learning algorithm to use (knn or rf).")

# Parse command line arguments
args = parser.parse_args()

# Convert bot color to chess.Color
bot_color = chess.WHITE if args.bot_color == "white" else chess.BLACK

# Create ChessStudent and ChessMatch instances
chess_student = ChessStudent(games_directory=args.games_directory, player_name=args.player_name, cache=args.cache, algorithm=args.algorithm)
chess_match = ChessMatch(chess_student, bot_color=bot_color)

# Play the game
chess_match.play_game()

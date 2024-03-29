import argparse
import random

import chess
import chess.svg

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
        self.user_color = chess.WHITE if bot_color == chess.BLACK else chess.BLACK

    @staticmethod
    def move_to_uci(move_indices):
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
        turn = board.turn
        fen = ChessStudent.fen_to_encoded_list(fen=fen, turn=turn)
        move_indices = self.chess_student.bot.predict([fen])[0]
        move = ChessMatch.move_to_uci(move_indices)
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
        counter_moves = 0
        while not board.is_game_over():
            print("")
            is_bot_turn = board.turn == self.bot_color
            if is_bot_turn:
                move = self.make_move(board)
                logger.info(f"Bot's move: {move.uci()}")
                board.push(move)
            else:
                move = input("Enter your move: ")
                try:
                    board.push_uci(move)
                except:
                    logger.warning(f"Ilegal move made: {move}. Try again.")
                    continue

            # Print board from the user perspective
            board_str = board.unicode(borders=True, empty_square=" ", orientation=self.user_color, invert_color=self.bot_color)
            board_str = board_str.replace("|", " |").replace("-----------------", "---------------------------")
            board_str = (board_str
                .replace("a", " a")
                .replace("b", " b")
                .replace("c", " c")
                .replace("d", " d")
                .replace("e", " e")
                .replace("f", " f")
                .replace("g", " g")
                .replace("h", " h")
            )
            print(f"Board state:\n{board_str}")

            # Save the board to an SVG file
            svg_content = chess.svg.board(board=board, flipped=self.user_color)
            with open(f"{self.chess_student.algorithm}_{counter_moves}.svg", "w") as svg_file:
                svg_file.write(svg_content)
            counter_moves += 1

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

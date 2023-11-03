import os

import chess
import chess.pgn
from sklearn.neighbors import KNeighborsClassifier

from cache_data import cache_data
from logger import setup_logging

# Set up the logging configuration
logger = setup_logging()


class ChessStudent:
    def __init__(self, games_directory: str, player_name: str, cache: bool = False):
        """
        Initializes the ChessStudent instance.
        
        :param games_directory: The directory where the PGN games files are stored.
        :type games_directory: str
        :param player_name: The name of the player that the algorithm should learn moves from.
        :type player_name: str
        :param cache: Parameter indicating if cache will be used.
        :type cache: bool
        """
        self._games_directory = games_directory
        self._player_name = player_name

        # Moves mapping
        self.piece_to_int = {
            'p': 1, 'r': 2, 'n': 3, 'b': 4, 'q': 5, 'k': 6,
            'P': -1, 'R': -2, 'N': -3, 'B': -4, 'Q': -5, 'K': -6
        }

        # Games loaded
        self._games = []

        # Algorithm trained
        self.clf = cache_data(func=self._train_classifier, file_name="algorithm", cache=cache)

    def _load_games(self):
        """
        Loads the PGN game files from the specified directory and parses the games.
        """
        # Get matches files
        files = os.listdir(self._games_directory)
        files = [file for file in files if file.endswith('.pgn')]
        logger.info(f"Number of files found in {self._games_directory}: {len(files)}")

        # Parse matches
        for file in files:
            with open(os.path.join('matches', file)) as file_content:
                logger.debug(f"Parsing match in the file: {file}")
                game = chess.pgn.read_game(file_content)
                game_variant = game.headers.get("Variant", None)
                if game_variant is None:
                    self._games.append(game)
        
        logger.info(f"Number of games parsed: {len(self._games)}")

    def _train_classifier(self):
        """
        Extracts training data from the loaded games, preprocesses the data, and trains the k-NN classifier.
        """
        # Load games
        self._load_games()

        # Extract data
        board_positions, moves = self._extract_training_data()
        board_positions = [self.fen_to_encoded_list(fen.replace('/', '').replace(' ', '')) for fen in board_positions]
        moves = [self._move_to_encoded_list(move) for move in moves]

        # Train algorithm
        algorithm = KNeighborsClassifier(n_neighbors=1)
        algorithm.fit(board_positions, moves)
        return algorithm

    def _extract_training_data(self):
        """
        Extracts training data from the loaded games.
        
        :return: A tuple (board_positions, moves) where board_positions is a list of board positions (FEN strings) and moves is a list of moves (UCI strings).
        :rtype: tuple(list, list)
        """
        # List to store board positions (FEN strings)
        board_positions = []

        # List to store moves (UCI strings)
        moves = []
        
        # Extract data from the games
        for game in self._games:
            board_init_pos = game.headers.get("FEN", None)
            board = chess.Board(board_init_pos) if board_init_pos is not None else chess.Board()
            # Determine if the target player is playing as white or black
            white_player = game.headers["White"]
            is_white = (white_player == self._player_name)
            # Iterate over the moves made in the game
            for move in game.mainline_moves():
                # Check if the current move was made by the target player
                if (board.turn == chess.WHITE and is_white) or (board.turn == chess.BLACK and not is_white):
                    # Append current board position (FEN string) to board_positions
                    board_positions.append(board.board_fen())
                    # Append move (UCI string) to moves
                    moves.append(move.uci())
                try:
                    # Update board to new state by applying the move
                    board.push(move)
                except AssertionError as excep:
                    game_link = game.headers["Link"]
                    logger.error(f"The next game contain an invalid move: {game_link} - {excep}")
        return board_positions, moves

    def fen_to_encoded_list(self, fen):
        """
        Converts a FEN string to a list of integers.
        
        :param fen: The FEN string to convert.
        :type fen: str
        :return: A list of integers representing the FEN string.
        :rtype: list
        """
        encoded = []
        for char in fen:
            if char.isdigit():
                encoded.extend([0] * int(char))
            elif char in self.piece_to_int:
                encoded.append(self.piece_to_int[char])
        return encoded

    def _move_to_encoded_list(self, move):
        """
        Converts a UCI move string to a list of integers.
        
        :param move: The UCI move string to convert.
        :type move: str
        :return: A list of integers representing the move.
        :rtype: list
        """
        start_square, target_square = move[:2], move[2:4]
        start_index = (int(start_square[1]) - 1) * 8 + ord(start_square[0]) - ord('a')
        target_index = (int(target_square[1]) - 1) * 8 + ord(target_square[0]) - ord('a')
        return [start_index, target_index]

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

import chess
import chess.pgn
import os
from sklearn.neighbors import KNeighborsClassifier
import random

piece_to_int = {
    'p': 1,
    'r': 2,
    'n': 3,
    'b': 4,
    'q': 5,
    'k': 6,
    'P': -1,
    'R': -2,
    'N': -3,
    'B': -4,
    'Q': -5,
    'K': -6
}

# List all the .pgn files in the 'matches' folder
files = os.listdir('matches')
files = [f for f in files if f.endswith('.pgn')]
print(f"Number of files: {len(files)}")

# Load the PGN files and parse the games
games = []
for file in files:
    with open(os.path.join('matches', file)) as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            games.append(game)

# Create a list of training examples (board positions and moves)
X = []
Y = []
for game in games:
    board = chess.Board()
    for move in game.mainline_moves():
        X.append(board.board_fen())
        Y.append(move.uci())
        board.push(move)

def fen_to_encoded_list(fen):
    encoded = []
    for char in fen:
        if char.isdigit():
            encoded.extend([0] * int(char))
        elif char in piece_to_int:
            encoded.append(piece_to_int[char])
        # Ignore other characters (e.g., '/', ' ')
    return encoded

def move_to_encoded_list(move):
    # Get the starting square and target square
    start_square, target_square = move[:2], move[2:4]
    # Convert the squares to indices
    start_index = (8 - int(start_square[1])) * 8 + ord(start_square[0]) - ord('a')
    target_index = (8 - int(target_square[1])) * 8 + ord(target_square[0]) - ord('a')
    # Return the encoded move
    return [start_index, target_index]


# Convert the training examples to a format suitable for the k-NN classifier
X = [fen_to_encoded_list(fen.replace('/', '').replace(' ', '')) for fen in X]
Y = [move_to_encoded_list(move) for move in Y]

# Train the k-NN classifier
clf = KNeighborsClassifier(n_neighbors=1)
clf.fit(X, Y)

# Define a function to convert a move represented as a list of indices to UCI format
def move_to_uci(move_indices):
    # Convert the indices to squares
    start_square = chess.square_name(move_indices[0])
    target_square = chess.square_name(move_indices[1])
    # Return the UCI move string
    return start_square + target_square

# Define a function to make a move based on the k-NN classifier
def make_move(board):
    fen = board.board_fen()
    fen = fen_to_encoded_list(fen.replace('/', '').replace(' ', ''))
    move_indices = clf.predict([fen])[0]
    move = move_to_uci(move_indices)
    move = chess.Move.from_uci(move)
    if move not in board.legal_moves:
        # If the move is not legal, choose a random legal move
        move = random.choice(list(board.legal_moves))
    return move

# Play a game against the bot
board = chess.Board()
while not board.is_game_over():
    if board.turn == chess.WHITE:
        # Player's turn
        move = input('Enter your move: ')
        board.push_uci(move)
    else:
        # Bot's turn
        move = make_move(board)
        print(f"Bot's move: {move.uci()}")
        board.push(move)

# Print the result of the game
print(board.result())

# Chess player simulator

## _Train and simulate the chess player's style_

This project is designed to simulate the playing style of a specific chess player. It achieves this by first downloading historical matches of the given player from _Chess.com_. These matches are then used to train a machine learning algorithm. Once trained, the algorithm can be used to predict and simulate the player's behavior in various chess scenarios.

[![Chess.com Logo](https://avatars.githubusercontent.com/u/577023?s=280&v=4)](https://www.chess.com/)

> Note: Notice that the project contains a `requirements.txt` file.

## Downloader

The `downloader.py` script is used to download chess games of a particular player from Chess.com and store them as PGN (Portable Game Notation) files. The script takes the following command-line arguments:

- `--username`: The username of the chess player whose games you want to download. Defaults to "Joseda8".
- `--year`: The year of the games to download. Defaults to the current year.
- `--remove`: If specified, removes existing PGN files in the `matches` folder before downloading new ones.
- `--folder`: The folder where the PGN files will be stored. Defaults to "matches".

To use the script, navigate to the project folder in a terminal and run the following command:

```sh
python downloader.py --username <player_name> --year <year> --remove --folder <folder_name>
```

For example, to download games from the year 2023 for the player "Joseda8" and store them in the "matches" folder, run the following command:

```sh
python downloader.py --username Joseda8 --year 2023
```


# Chess player

## ChessStudent
The `ChessStudent` class is used to train a machine learning model that predicts chess moves based on historical games. The class supports two different machine learning algorithms for predicting moves: `k-Nearest Neighbors (k-NN)` and `Random Forest`. The trained model can be used to simulate the playing style of a specific chess player.

## ChessMatch
The `ChessMatch` class is used to play a game of chess against the bot trained by the `ChessStudent` class. It generates moves for the bot based on the trained model and plays the game until a game-over state is reached.

The script takes the following command-line arguments:

- `--games_directory`: The directory where the PGN games files are stored.
- `--player_name`: The name of the player that the bot should learn moves from.
- `--cache`: Indicates whether the results should be cached or read from the cache.
- `--bot_color`: The color that the bot is playing as (either "white" or "black"). Defaults to white.
- `--algorithm`: The machine learning algorithm to use (either "knn" or "rf"). Defaults to knn.

To use the script, navigate to the project folder in a terminal and run the following command:

```sh
python main.py --games_directory <path_to_games_directory> --player_name <player_name> --cache --bot_color <bot_color> --algorithm <algorithm>
```

For example, to play a game of chess against the bot trained on games from the "matches" folder for the player "Joseda8", with the bot playing as white and using the k-NN algorithm, run the following command:

```sh
python main.py --games_directory matches --player_name Joseda8 --cache --bot_color white --algorithm knn
```

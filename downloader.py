import argparse
import cloudscraper
import logging
import os


# Set up the logging configuration
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class ChessDownloader:
    """
    This class is used to download chess games of a particular player from 
    Chess.com and store them as PGN (Portable Game Notation) files.
    """

    def __init__(self, player_name: str, folder: str):
        """
        Initializes the ChessDownloader instance.

        :param player_name: The name of the chess player whose games to download.
        :type player_name: str
        :param folder: The folder where the PGN files will be stored.
        :type folder: str
        """
        self._player_name = player_name
        self._folder = folder

        # Module to make requests bypassing Cloudflare's anti-bot
        self._scraper = cloudscraper.create_scraper()

    def _store_match(self, match_url: str, match_pgn: str):
        """
        Stores the match PGN data in a file.

        :param match_url: The URL of the match.
        :type match_url: str
        :param match_pgn: The PGN data of the match.
        :type match_pgn: str
        """
        match_id = match_url.split("/")[-1]
        with open(f"{self._folder}/{match_id}.pgn", "a") as file:
            logging.debug(f"Stored match: {match_url}")
            file.write(match_pgn)

    def _store_matches(self, url_match: str):
        """
        Fetches the match data from the given URL and stores the matches.

        :param url_match: The URL of the matches.
        :type url_match: str
        """
        logging.debug(f"Fetching matches from {url_match}")
        # Request matches
        response = self._scraper.get(url_match)
        if response.status_code == 200:
            data = response.json()
            matches = data["games"]
            logging.info(f"Total matches to store: {len(matches)}")
            # Store matches
            for match in matches:
                self._store_match(
                    match_url=match["url"], match_pgn=match["pgn"])
        else:
            logging.warning(f"There was an error downloading the matches from {url_match}")

    def fetch_games(self, year: int):
        """
        Fetches the games of the specified year and stores them as PGN files.

        :param year: The year of the games to download.
        :type year: int
        """
        logging.info(f"Fetching games for the year {year}")
        # Create the 'matches' folder if it doesn't exist
        if not os.path.exists(self._folder):
            os.makedirs(self._folder)

        # Download all the games for a given year per month
        for month in range(1, 13):
            month_name = {
                1: 'January', 2: 'February', 3: 'March', 4: 'April',
                5: 'May', 6: 'June', 7: 'July', 8: 'August',
                9: 'September', 10: 'October', 11: 'November', 12: 'December'
            }[month]
            logging.info(f"Fetching games for {month_name}")
            url_match = f"https://api.chess.com/pub/player/{self._player_name}/games/{year}/{month:02d}"
            self._store_matches(url_match=url_match)


# Argument parser
parser = argparse.ArgumentParser(
    description='Download chess games and store them as PGN files.')
parser.add_argument('--username', type=str, default='Joseda8', help='Username of the chess player.')
parser.add_argument('--year', type=int, default=2023, help='Year of the games to download.')
parser.add_argument('--remove', action='store_true', default=False, help='Remove existing files before downloading.')
parser.add_argument('--folder', type=str, default='matches', help='Folder to store the PGN files.')

# Parse the arguments
args = parser.parse_args()

# Remove existing files if the --remove flag is set
if args.remove and os.path.exists(args.folder):
    for filename in os.listdir(args.folder):
        file_path = os.path.join(args.folder, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)

# ChessDownloader instance
chess_downloader = ChessDownloader(player_name=args.username, folder=args.folder)
chess_downloader.fetch_games(year=args.year)

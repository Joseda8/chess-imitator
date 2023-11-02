import os
import pickle
import threading

from typing import Callable

from logger import setup_logging

# Set up the logging configuration
logger = setup_logging()


# Constant to specify the folder to store cached files
CACHE_FOLDER = "cache_data"
CACHE_LOCK = threading.Lock()


def cache_data(func: Callable, file_name: str, cache: bool, *args, **kwargs):
    """
    Caches the result of a function call in a file.

    :param func: The function that you want to cache the result of.
    :param file_name: The name of the file where the cached data will be stored (without extension).
    :param cache: A boolean flag that indicates whether caching should be enabled or not.
    :param *args: Arguments for the callback.
    :param **kwargs: Keyword arguments for the callback.

    :return: The data from the function.
    """

    computed_data = None

    if cache:
        # Use a lock to ensure thread safety when creating the cache folder
        with CACHE_LOCK:
            try:
                # Create the cache folder if it doesn't exist
                if not os.path.exists(CACHE_FOLDER):
                    os.makedirs(CACHE_FOLDER)
            except Exception as excep:
                logger.error(f"Error when creating folder: {excep}")

        # Add the cache folder path and the .pickle extension to the file_name
        cache_file_path = os.path.join(CACHE_FOLDER, f"{file_name}.pickle")

        # Check if the file already exists
        file_exist = os.path.isfile(cache_file_path)
        if file_exist:
            # If the file exists, load the data from it using pickle
            with open(cache_file_path, "rb") as cache_file:
                logger.info(f"Load cache from {cache_file_path}!")
                computed_data = pickle.load(cache_file)

        else:
            # Call the function to compute the data
            computed_data = func(*args, **kwargs)

            # Write the computed data to the cache file using pickle
            with open(cache_file_path, "wb") as cache_file:
                logger.info(f"Write cache to {cache_file_path}")
                pickle.dump(computed_data, cache_file)

    else:
        # Call the function to compute the data
        computed_data = func(*args, **kwargs)

    return computed_data
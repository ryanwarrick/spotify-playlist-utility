import configparser
import os
from pathlib import Path
from spotify_playlist_utility.Spotify import SpotifyManager
import pprint
import argparse


def load_config_parser(config_filepath):
    # Load standard config.ini file if config file not provided
    if config_filepath is None:
        config_filepath = os.path.join(get_project_root(), "config.ini")

    # Create the configuration parser
    config_parser = configparser.ConfigParser()

    # Read the configuration file
    config_parser.read(config_filepath)

    return config_parser


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "-c", "--config", action='store', help="Specify filepath for custom config file", )
    argument_parser.add_argument(
        "-s", "--export-saved-tracks", nargs="?", default=None, const='const',
        help="Will generate a .CSV listing the user's saved tracks.")
    argument_parser.add_argument(
        "-i", "--create-playlist", action='store', help="Create a Spotify playlist using the data and file name from a .CSV at the given filepath")
    args = argument_parser.parse_args()

    # Process config file argument and load config parser
    config_parser = load_config_parser(args.config)

    # Build SpotifyManager object with config_parser help
    SpotifyMgr = SpotifyManager(config_parser)

    # Execute appropriate logic per specified optional argument
    if args.export_saved_tracks:
        filepath = args.export_saved_tracks
        SpotifyMgr.export_saved_tracks(filepath)

    if args.create_playlist:
        filepath = args.create_playlist
        SpotifyMgr.import_tracks_as_playlist(filepath)


def get_project_root() -> Path:
    return Path(__file__).parent


if __name__ == "__main__":
    main()

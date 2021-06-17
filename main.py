import configparser
import os
import sys
from pathlib import Path
from spotify_playlist_utility.Spotify import SpotifyManager
import pprint


def load_config_parser():
    config_filepath = os.path.join(get_project_root(), "config.ini")
    arguments = sys.argv
    if len(arguments) > 1:
        arguments = arguments[1:]
        config_filepath = arguments[0]

    # Create the configuration parser
    config_parser = configparser.ConfigParser()

    # Read the configuration file
    config_parser.read(config_filepath)

    return config_parser


def main():
    config_parser = load_config_parser()
    # print(config_parser["DEFAULT"]["SpotipyClientID"])

    SpotifyMgr = SpotifyManager(config_parser)

    # Testing: get_playlists()
    # pprint.pprint(SpotifyMgr.get_playlists())

    # Testing: get_saved_tracks()
    saved_tracks = SpotifyMgr.get_saved_tracks()
    for i, saved_track in enumerate(saved_tracks):
        print("### {0} ###".format(i))
        pprint.pprint(saved_track)


def get_project_root() -> Path:
    return Path(__file__).parent


if __name__ == "__main__":
    main()

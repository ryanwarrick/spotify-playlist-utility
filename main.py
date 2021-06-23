import argparse
import configparser

from spotify_playlist_utility.Spotify import SpotifyManager

# TODO: Remove temp files and those files no longer needed from proj root dir


def load_config_parser(config_file_path) -> configparser.ConfigParser:
    # Create the configuration parser
    config_parser = configparser.ConfigParser()

    # Read the configuration file
    config_parser.read(config_file_path)

    return config_parser


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "config",
        help="Specify file path to the script's config file (see README.md)."
    )
    argument_parser.add_argument(
        "-s", "--export-saved-tracks",
        nargs="?", default=None, const='const',
        help=("Generate a .csv listing of the user's saved tracks and save "
              "to the specified file path (If not specified, default: "
              ".\data.csv).")
    )
    argument_parser.add_argument(
        "-p", "--export-playlist-tracks",
        nargs="?", default=None, const='const',
        help=("Generate a .csv listing of the specified playlist's tracks "
              "and save to the specified file path (if not specified, "
              "default: .\data.csv).")
    )
    argument_parser.add_argument(
        "-c", "--create-playlist",
        action='store',
        help=("Generate a playlist using the name and data of a .csv at "
              "the specified file path (format must match that of exported "
              ".csv files).")
    )
    argument_parser.add_argument(
        "-l", "--list-playlists",
        action='store_true',
        help="List playlists of the spotify account."
    )
    argument_parser.add_argument(
        "-z", "--shuffle-playlist",
        action='store_true',
        help="Shuffles the track order of a selected spotify playlist."
    )
    # argument_parser.add_argument(
    #     "-a", "--export-all-playlists",
    #     nargs="?", default=None, const='const',
    #     help=("Generate .csv listings of tracks for each of the user's "
    #           "playlist's tracks and save to the specified directory (if not specified, "
    #           "default: .\all_playlists\).")
    # TODO: Add export-all-playlists functionality
    # add ending '\' logic (for if there OR not)
    # build out the directory creation logic
    # copy and repurpose the export_playlist_tracks function to do as is, just iterate through all playlists
    # )
    args = argument_parser.parse_args()

    print("(Note: If at any time you see following prompt, 'Enter the URL you "
          "were redirected to', then comply by copy/pasting the URL into the "
          "terminal prompt. This is per Spotify API authentication purposes.)")

    # Load config parser at specified file path
    config_parser = load_config_parser(args.config)

    # Build SpotifyManager object with config_parser's help
    SpotifyMgr = SpotifyManager(config_parser)

    # Execute appropriate logic per specified optional argument
    if args.export_saved_tracks:
        SpotifyMgr.export_saved_tracks(args.export_saved_tracks)
    elif args.export_playlist_tracks:
        SpotifyMgr.export_playlist_tracks(args.export_playlist_tracks)
    elif args.create_playlist:
        SpotifyMgr.create_playlist(args.create_playlist)
    elif args.list_playlists:
        SpotifyMgr.list_playlists()
    elif args.shuffle_playlist:
        SpotifyMgr.shuffle_playlist()
    else:
        print("No function arguments were passed, therefore script did not "
              "take any actions.")


if __name__ == "__main__":
    main()

import random
from pathlib import Path
import typing
import configparser

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from spotify_playlist_utility.Track import Track
from spotify_playlist_utility.TrackLists import Playlist, TrackListing


class SpotifyManager(object):
    def __init__(self, config_parser: configparser.ConfigParser):
        self.config_parser = config_parser
        self.authorized = False
        self.sp = None

    def authorize(self, scope_set: str) -> None:
        if not self.authorized:
            auth_manager = SpotifyOAuth(client_id=self.config_parser["DEFAULT"]
                                        ["SpotipyClientID"],
                                        client_secret=self.config_parser["DEFAULT"]
                                        ["SpotipyClientSecret"],
                                        redirect_uri=self.config_parser["DEFAULT"]
                                        ["RedirectURI"],
                                        scope=self.config_parser["Scopes"]
                                        [scope_set])
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            self.authorized = True

    def build_track_object_from_data(self, data: dict) -> Track:
        """Returns a Track object from a provided dict data

        Args:
            data (dict): Dictionary representing representing a Spotify
        API "TrackObject"

        Returns:
            Track: Track object capturing key elements of dict data
        """
        uri = data["uri"]
        name = data["name"]
        artist = data["artists"][0]["name"]
        album = data["album"]["name"]
        track = Track(uri, name, artist, album)
        return track

    def get_saved_tracks(self) -> TrackListing:
        """
        Generate a TrackListing of the user's saved tracks.

        Called by argument: "-s/--export-saved-tracks".

        Returns:
            TrackListing: TrackListing object storing a list of saved tracks.
        """
        saved_tracks = TrackListing()
        saved_tracks_response = self.sp.current_user_saved_tracks()
        while saved_tracks_response:
            for saved_track_data in saved_tracks_response['items']:
                saved_track_data = saved_track_data['track']
                saved_track = self.build_track_object_from_data(
                    saved_track_data)
                saved_tracks.tracks.append(saved_track)
            if saved_tracks_response['next']:
                saved_tracks_response = self.sp.next(saved_tracks_response)
            else:
                saved_tracks_response = None
        return saved_tracks

    def export_saved_tracks(self, file_path: str) -> None:
        """
        Generate a .csv listing of the user's saved tracks and save to the
        specified file path (If not specified, default: .\data.csv).

        Called by argument: "-s/--export-saved-tracks".

        Args:
            file_path (string): File path pointing at where to save the generated .csv file.
        """
        self.authorize("ExportSavedTracks")
        saved_tracks = self.get_saved_tracks()
        saved_tracks.export_tracks(file_path)

    def get_playlists(self) -> typing.List[Playlist]:
        """
        Fetches playlists from the user's playlists. Creates data objects from
        the resulting playlists.

        Called by arguments:
            "-p"/"--export-playlist-tracks"
            "-l"/"--list-playlists"
            "-z"/"--shuffle-playlist"

        Returns:
            typing.List[Playlist]:  List of playlist objects representing the
            user's playlists.
        """
        playlists = []
        playlist_response = self.sp.current_user_playlists()
        while playlist_response:
            for playlist_data in playlist_response['items']:
                playlist = Playlist(
                    uri=playlist_data['uri'], name=playlist_data['name'], description=playlist_data['description'], reported_length=playlist_data['tracks']['total'])
                playlists.append(playlist)
            if playlist_response['next']:
                playlist_response = self.sp.next(playlist_response)
            else:
                playlist_response = None
        return playlists

    def list_playlists(self) -> typing.List[Playlist]:
        """
        Lists playlists in the console with indexing for user selection
        purposes.

        Called by arguments:
            "-p"/"--export-playlist-tracks"
            "-l"/"--list-playlists"
            "-z"/"--shuffle-playlist"

        Returns:
            typing.List[Playlist]: List of Playlist objects representing the
            user's playlists.
        """
        self.authorize("ListPlaylists")

        playlists = self.get_playlists()

        column_titles = ['Index', 'Name', 'Track Count']

        playlist_indicies_for_table_printing = [
            str(x) for x in range(0, len(playlists))
        ]
        playlist_names_for_table_printing = [
            playlist.name for playlist in playlists
        ]
        playlist_track_counts_for_table_printing = [
            str(playlist.reported_length) for playlist in playlists
        ]

        column_length_maximums = [
            max(len(column_titles[0]),
                len(max(playlist_indicies_for_table_printing, key=len))
                ),
            max(len(column_titles[1]),
                len(max(playlist_names_for_table_printing, key=len))
                ),
            max(len(column_titles[2]),
                len(max(playlist_track_counts_for_table_printing, key=len))
                )
        ]

        data_for_table_printing = [column_titles] + list(zip(
            playlist_indicies_for_table_printing,
            playlist_names_for_table_printing,
            playlist_track_counts_for_table_printing
        ))

        for row_index, data in enumerate(data_for_table_printing):
            line_parts = []
            for column_index, value in enumerate(data):
                line_parts.append(str(value).ljust(
                    column_length_maximums[column_index]+1))
            line = '|'.join(line_part for line_part in line_parts)
            print(line)
            if row_index == 0:
                print('-' * len(line))

        return playlists

    def playlist_picker(self) -> Playlist:
        """
        Lists user's playlists. Prompts for numeric selection for desired
        playlist selection.

        Called by arguments:
            "-p"/"--export-playlist-tracks"
            "-z"/"--shuffle-playlist"


        Returns:
            Playlist: Returns Playlist object of selected playlist per input.
        """
        playlists = self.list_playlists()
        playlist_choice_input = input("Please provide chosen playlist index: ")
        return playlists[int(playlist_choice_input)]

    def get_playlist(self, playlist_id: str) -> Playlist:
        """
        Fetches Playlist object and populates the instance's 'tracks'
        variable with the playlist's tracks.

        Called by argument:
            "-p"/"--export-playlist-tracks"
            "-z"/"--shuffle-playlist"

        Args:
            playlist_id (str): ID of desired playlist.

        Returns:
            Playlist: Playlist object with populated 'tracks' instance variable per playlist's contents.
        """

        playlist_response = self.sp.playlist(playlist_id)
        playlist = Playlist(
            uri=playlist_response["uri"],
            name=playlist_response["name"],
            description=playlist_response["description"],
            reported_length=playlist_response["tracks"]["total"]
        )
        playlist_tracks_response = self.sp.playlist_items(playlist.id)

        # playlist.uri = playlist_tracks_response
        while playlist_tracks_response:
            for playlist_track_data in playlist_tracks_response['items']:
                playlist_track = self.build_track_object_from_data(
                    playlist_track_data['track'])
                playlist.tracks.append(playlist_track)
            if playlist_tracks_response['next']:
                playlist_tracks_response = self.sp.next(
                    playlist_tracks_response)
            else:
                playlist_tracks_response = None
        return playlist

    def export_playlist_tracks(self, filepath: str) -> None:
        """
        Generate a .csv listing of the specified playlist's tracks and save to
        the specified file path (if not specified, default: .\data.csv).

        Called by argument: "-p"/"--export-playlist-tracks"

        Args:
            filepath (str): File path pointing at where to save the generated .csv file.
        """
        self.authorize("ExportPlaylistTracks")
        playlist = self.playlist_picker()
        # Overwrite variable such that it holds a Playlist object populated with tracks, instead of a 'shell' playlist object.
        playlist = self.get_playlist(playlist.id)
        playlist.export_tracks(filepath)

    def create_playlist(self, filepath: str) -> str:
        """
        "Generate a playlist using the name and data of a .csv at "
              "the specified file path (format must match that of exported "
              ".csv files).")

        Args:
            filepath (str): File path to .csv file listing desired
            tracks to include in new playlist (format must match that of exported .csv files)

        Returns:
            str: ID of newly generated playlist
        """
        self.authorize("CreateEditPlaylist")
        imported_tracks = TrackListing()
        imported_tracks.import_tracks(filepath)
        imported_tracks.tracks = imported_tracks.tracks

        name = Path(filepath).stem

        playlist_id = self.sp.user_playlist_create(
            self.config_parser['DEFAULT']['UserID'], name, public=False)['id']

        track_ids = [
            imported_track.uri for imported_track in imported_tracks.tracks]
        random.shuffle(track_ids)

        track_id_chunks = self.chunk_list(track_ids, 100)

        for track_id_chunk in track_id_chunks:
            self.sp.playlist_add_items(playlist_id, track_id_chunk)

        return playlist_id

    def shuffle_playlist(self) -> None:
        """
        Shuffles the track order of a selected spotify playlist.
        """
        self.authorize("ShufflePlaylist")
        playlist = self.playlist_picker()
        # Overwrite variable such that it holds a Playlist object populated with tracks, instead of a 'shell' playlist object.
        playlist = self.get_playlist(playlist.id)

        for i, playlist_track in enumerate(playlist.tracks):
            insert_before = random.randint(0, len(playlist.tracks)-1)
            self.sp.playlist_reorder_items(
                playlist.id, i,
                insert_before,
                range_length=1,
                snapshot_id=None
            )

    def chunk_list(self, list, n):
        return [list[i:i + n] for i in range(0, len(list), n)]

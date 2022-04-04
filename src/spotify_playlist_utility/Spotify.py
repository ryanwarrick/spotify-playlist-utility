import configparser
import random
import sys
import typing
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from spotify_playlist_utility.Track import Track
from spotify_playlist_utility.TrackLists import Playlist, TrackListing


class SpotifyManager(object):

    # Define 'Scopes' class attrs for proper permission scoping of API calls.
    # Scopes set on a per-function basis - principle of least privilege.
    SCOPES = {
        'ExportSavedTracks':
            'user-library-read',
        'ExportPlaylistTracks':
            'playlist-read-private, playlist-read-collaborative',
        'CreateEditPlaylist': 'playlist-modify-private',
        'ListPlaylists':
            'playlist-read-private, playlist-read-collaborative',
        'ShufflePlaylistTracks':
            'playlist-read-private, playlist-read-collaborative, playlist-modify-private'
    }

    def __init__(self, config_parser: configparser.ConfigParser):
        """[summary]

        :param config_parser: [description]
        :type config_parser: configparser.ConfigParser
        """
        self.config_parser = config_parser
        self.authorized = False
        self.sp = None
        self.user_id = None

    def authorize(self, scope_set: str) -> None:
        if not self.authorized:
            auth_message = ("\n-------\nNote: If valid session was not "
                            "previously cached, then the spotipy library will "
                            "open a web browser to authorize the user. If "
                            "script flow pauses, check your browser for the "
                            "challenge. Review the permissions and 'Agree' to "
                            "authorize the app you previously created on "
                            "Spotify's developer site per the README.md"
                            "('SetupConfig' section).\n-------\n")
            print(auth_message)
            auth_manager = SpotifyOAuth(
                client_id=self.config_parser["DEFAULT"]["ClientID"],
                client_secret=self.config_parser["DEFAULT"]["ClientSecret"],
                redirect_uri=self.config_parser["DEFAULT"]
                ["RedirectURI"],
                scope=SpotifyManager.SCOPES[scope_set],
                open_browser=True
            )
            """
                Note on 'open_browser' argument above:
                Change to False so that console provides URL to navigate to.
                Then, one enters the URL they were redirected to.
                'False' works, but I find 'True' to be more clear for end user.
            """

            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            self.authorized = True
            self.user_id = self.sp.me()['id']

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
            "-z"/"--shuffle-playlist-tracks"

        Returns:
            typing.List[Playlist]:  List of playlist objects representing the
            user's playlists.
        """
        playlists = []
        current_user_playlists_response = self.sp.current_user_playlists()
        while current_user_playlists_response:
            for playlist_data in current_user_playlists_response['items']:
                '''
                Per my testing, the '/v1/me/playlists' endpoint 
                ('current_user_playlists' spotipy function) is currently 
                buggy when reporting track count for returned playlists. I'm 
                unclear as to why, but when I create valid playlists with this 
                script, they sometimes get reported as having a length of 0 in 
                response to the above API endpoint call. If I drill down into 
                each playlist using '/v1/playlists/{playlist_id}' ('playlist' 
                spotipy function), then the reported tracks total is accurate.

                Therefore, this logic is to work around that discrepancy by 
                making a call to the '/v1/playlists/{playlist_id}' for each 
                received playlist to grab the tracks count.
                '''
                playlist_response = self.sp.playlist(playlist_data['id'])
                track_count = playlist_response['tracks']['total']

                '''
                Now to continue on building the Playlist objects using the 
                track_count specially captured via the call above (because of track count errors in playlist_data) and all other values captured within the playlist_data object
                '''
                playlist = Playlist(
                    uri=playlist_data['uri'], name=playlist_data['name'], description=playlist_data['description'], track_count=track_count)
                playlists.append(playlist)
            if current_user_playlists_response['next']:
                current_user_playlists_response = self.sp.next(
                    current_user_playlists_response)
            else:
                current_user_playlists_response = None
        return playlists

    def list_playlists(self) -> typing.List[Playlist]:
        """
        Lists playlists in the console with indexing for user selection
        purposes.

        Called by arguments:
            "-p"/"--export-playlist-tracks"
            "-l"/"--list-playlists"
            "-z"/"--shuffle-playlist-tracks"

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
            str(playlist.track_count) for playlist in playlists
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

        print("")
        for row_index, data in enumerate(data_for_table_printing):
            line_parts = []
            for column_index, value in enumerate(data):
                line_parts.append(str(value).ljust(
                    column_length_maximums[column_index]+1))
            line = '|'.join(line_part for line_part in line_parts)
            print(line)
            if row_index == 0:
                print('-' * len(line))
        print("")

        return playlists

    def playlist_picker(self) -> Playlist:
        """
        Lists user's playlists. Prompts for numeric selection for desired
        playlist selection.

        Called by arguments:
            "-p"/"--export-playlist-tracks"
            "-z"/"--shuffle-playlist-tracks"


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
            "-z"/"--shuffle-playlist-tracks"

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
            track_count=playlist_response["tracks"]["total"]
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

    def import_tracks_to_playlist(self, filepath: str) -> str:
        """
        Generate a playlist using the name and data of a .csv at the specified
        file path (format must match that of exported .csv files).

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
            self.user_id, name, public=False)['id']

        print(
            "Tracks Import File uploaded as Spotify playlist with the following name: {0}".format(name))

        track_ids = [
            imported_track.uri for imported_track in imported_tracks.tracks]
        random.shuffle(track_ids)

        track_id_chunks = self.chunk_list(track_ids, 100)

        for track_id_chunk in track_id_chunks:
            self.sp.playlist_add_items(playlist_id, track_id_chunk)

        return playlist_id

    def shuffle_playlist_tracks(self) -> None:
        """
        Shuffles the track order of a selected spotify playlist.
        """
        self.authorize("ShufflePlaylistTracks")
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

        print("Shuffling complete on playlist: {0}".format(playlist.name))

    def export_saved_tracks_to_liked_memory_playlist(self) -> None:
        # Get liked songs
        self.authorize("ListPlaylists")
        saved_tracks = self.get_saved_tracks()

        # Get playlists to detect for liked memory playlist
        playlists = self.get_playlists()
        # list of all elements with .n==30
        liked_memory_playlist_list = [
            x for x in playlists if x.name == "Liked Memory"]

        liked_memory_playlist_id = None

        self.authorize("CreateEditPlaylist")

        # Create liked memory playlist, if it doesn't exist
        if not liked_memory_playlist_list:  # empty list
            liked_memory_playlist_id = self.sp.user_playlist_create(
                self.user_id, "Liked Memory", public=False)['id']

        elif len(liked_memory_playlist_list) == 1:
            liked_memory_playlist_id = liked_memory_playlist_list[0].id

        # Detect for too many matching playlists and exit if collision
        else:  # len(liked_memory_playlist_list) > 1
            sys.exit(
                "Too many playlists matching the 'Liked Memory' name found.... Don't know which one is correct. Exiting.")

        # Append saved tracks to liked memory playlist
        liked_memory_playlist = self.get_playlist(liked_memory_playlist_id)
        saved_tracks_to_append = []
        for saved_track in saved_tracks.tracks:
            if not any(liked_memory_track.uri == saved_track.uri for liked_memory_track in liked_memory_playlist.tracks):
                saved_tracks_to_append.append(saved_track)
        saved_track_to_append_ids = [
            saved_track_to_append.uri for saved_track_to_append in saved_tracks_to_append]

        saved_tracks_to_append_id_chunks = self.chunk_list(
            saved_track_to_append_ids, 100)

        for saved_track_to_append_id_chunk in saved_tracks_to_append_id_chunks:
            self.sp.playlist_add_items(
                liked_memory_playlist_id, saved_track_to_append_id_chunk, 0)

        return liked_memory_playlist_id

    def chunk_list(self, list, n):
        return [list[i:i + n] for i in range(0, len(list), n)]

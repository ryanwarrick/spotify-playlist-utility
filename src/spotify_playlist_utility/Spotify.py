import spotipy
from spotipy.oauth2 import SpotifyOAuth
import typing
from pathlib import Path
import os
import csv
import random


class Track():
    """
    Represents a single track within Spotify.
    """

    def __init__(self, uri, name, artist, album):
        self.uri = uri
        self.name = name
        self.artist = artist
        self.album = album

    def __str__(self):
        return "{0} by {1} on {2} - {3}".format(self.name, self.artist, self.album, self.uri)

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"{self.uri!r}, {self.name!r}, {self.artist!r}, {self.album!r})")

    def csv_export_row(self):
        dict = {'uri': self.uri, 'name': self.name,
                'artist': self.artist, 'album': self.album}
        return dict

    @staticmethod
    def csv_export_header():
        return ['uri', 'name', 'artist', 'album']


class TrackListing():
    def __init__(self, tracks: typing.List[Track] = []) -> None:
        self.tracks = tracks

    def __post_init__(self):
        if self.tracks == None:
            self.tracks = []

    def export_tracks(self, filepath) -> None:
        if filepath == 'const':
            filepath = os.path.join(
                self.get_project_root(), "saved_tracks_export.csv")
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = Track.csv_export_header()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for track in self.tracks:
                writer.writerow(track.csv_export_row())

    def import_tracks(self, filepath) -> None:
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                track = Track(row['uri'], row['name'],
                              row['artist'], row['album'])
                self.tracks.append(track)

    def get_project_root(self) -> Path:
        return Path(__file__).parent.parent.parent


class SpotifyManager(object):
    def __init__(self, config_parser):
        self.config_parser = config_parser
        self.sp = None

    def authorize(self, scope_set):
        auth_manager = SpotifyOAuth(client_id=self.config_parser["DEFAULT"]["SpotipyClientID"],
                                    client_secret=self.config_parser["DEFAULT"]["SpotipyClientSecret"],
                                    redirect_uri=self.config_parser["DEFAULT"]["RedirectURI"],
                                    scope=self.config_parser["Scopes"][scope_set])
        self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def get_playlists(self):
        self.authorize("GetPlaylists")
        playlists_data = []
        playlists_response = self.sp.current_user_playlists()
        while playlists_response:
            for i, playlist in enumerate(playlists_response['items']):
                # print("%4d %s %s" % (
                #     i + 1 + playlists_response['offset'], playlist['uri'],  playlist['name']))
                playlists_data.append(playlist)
            if playlists_response['next']:
                playlists_response = self.sp.next(playlists_response)
            else:
                playlists_response = None
        return playlists_data

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

    def get_saved_tracks(self) -> typing.List[Track]:
        # https://github.com/plamere/spotipy/blob/master/examples/show_my_saved_tracks.py
        self.authorize("GetSavedTracks")
        saved_tracks = []
        saved_tracks_response = self.sp.current_user_saved_tracks()
        while saved_tracks_response:
            for i, saved_track_data in enumerate(saved_tracks_response['items']):
                saved_track_data = saved_track_data['track']
                saved_track = self.build_track_object_from_data(
                    saved_track_data)
                saved_tracks.append(saved_track)
            if saved_tracks_response['next']:
                saved_tracks_response = self.sp.next(saved_tracks_response)
            else:
                saved_tracks_response = None
        return(saved_tracks)

    def export_saved_tracks(self, filepath) -> None:
        saved_tracks = TrackListing(self.get_saved_tracks())
        saved_tracks.export_tracks(filepath)

    def export_playlist_tracks(self, filepath, playlist_id) -> None:
        # TODO: Build out this function. Similar to export_saved_tracks, except it'd be pulling from a specific playlist id, not the "saved"
        pass

    def import_tracks_as_playlist(self, filepath) -> None:
        self.authorize("CreatePlaylist")
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

    def get_playlist_tracks(self):
        # https://github.com/plamere/spotipy/blob/master/examples/playlist_tracks.py
        pass

    def chunk_list(self, list, n):
        return [list[i:i + n] for i in range(0, len(list), n)]

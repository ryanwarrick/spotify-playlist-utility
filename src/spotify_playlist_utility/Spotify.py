import spotipy
from spotipy.oauth2 import SpotifyOAuth


class Track(object):
    def __init__(self, uri, name, artist, album):
        self.uri = uri
        self.name = name
        self.artist = artist
        self.album = album

    def __str__(self):
        return "{0} by {1} on {2} - {3}".format(self.name, self.artist, self.album, self.uri)


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

    def get_saved_tracks(self):
        self.authorize("GetSavedTracks")
        saved_tracks_data = []
        saved_tracks_response = self.sp.current_user_saved_tracks()
        while saved_tracks_response:
            for i, saved_track in enumerate(saved_tracks_response['items']):
                saved_track = saved_track['track']
                # print(
                #     "{0} - {1}".format(saved_track['name'], saved_track['artists'][0]['name']))
                saved_tracks_data.append(saved_track)
            if saved_tracks_response['next']:
                saved_tracks_response = self.sp.next(saved_tracks_response)
            else:
                saved_tracks_response = None
        return(saved_tracks_data)

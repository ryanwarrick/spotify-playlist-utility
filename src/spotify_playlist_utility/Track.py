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

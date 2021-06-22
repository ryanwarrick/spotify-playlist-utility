import csv
import os
import typing
from pathlib import Path

from spotify_playlist_utility.Track import Track


class TrackListing():
    def __init__(self, tracks: typing.List[Track] = []) -> None:
        self.tracks = tracks

    def export_tracks(self, file_path) -> None:
        if file_path == 'const':
            file_path = os.path.join(os.getcwd(), "data.csv")
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = Track.csv_export_header()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for track in self.tracks:
                writer.writerow(track.csv_export_row())

    def import_tracks(self, file_path) -> None:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                track = Track(row['uri'], row['name'],
                              row['artist'], row['album'])
                self.tracks.append(track)


class Playlist(TrackListing):
    def __init__(self, uri: str = None, name: str = None, description: str = None, tracks: typing.List[Track] = [], reported_length=None):
        super().__init__(tracks)
        self.uri = uri
        self.name = name
        self.description = description
        self.reported_length = reported_length
        self.id = uri.split(":")[-1]

    def __str__(self):
        format_string = "{0} - {1}"
        if self.tracks:
            return format_string.format(self.name, str(len(self.tracks)))
        else:
            return format_string.format(self.name, str(self.reported_length))

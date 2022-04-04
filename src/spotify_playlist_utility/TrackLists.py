import csv
import os
import sys
import typing

from spotify_playlist_utility.Track import Track


class TrackListing():
    def __init__(self, tracks: typing.List[Track] = []) -> None:
        self.tracks = tracks

    def export_tracks(self, file_path) -> None:
        if file_path == 'const':
            file_path = os.path.join(os.getcwd(), "data.csv")
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = Track.csv_export_header()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for track in self.tracks:
                    writer.writerow(track.csv_export_row())
            print(
                "Tracks Export File saved to the following path: {0}".format(file_path))
        except OSError:
            print("Operation Failed: Error writing to file.")
            sys.exit(1)

    def import_tracks(self, file_path) -> None:
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    track = Track(row['uri'], row['name'],
                                  row['artist'], row['album'])
                    self.tracks.append(track)
        except OSError:
            print("Operation Failed: Error reading from file.")
            sys.exit(1)


class Playlist(TrackListing):
    def __init__(self, uri: str = None, name: str = None, description: str = None, tracks: typing.List[Track] = [], track_count=None):
        super().__init__(tracks)
        self.uri = uri
        self.name = name
        self.description = description
        self.track_count = track_count
        self.id = uri.split(":")[-1]

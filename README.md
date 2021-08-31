<p align="center">
    <img alt="spotify-playlist-utility logo" src="https://github.com/ryanwarrick/spotify-playlist-utility/blob/master/docs/images/snakify.png?raw=true" height="100">
</p>

![license](https://img.shields.io/github/license/ryanwarrick/spotify-playlist-utility)
![GitHub last commit](https://img.shields.io/github/last-commit/ryanwarrick/spotify-playlist-utility)
[![GitHub issues](https://img.shields.io/github/issues/ryanwarrick/spotify-playlist-utility)](https://github.com/ryanwarrick/spotify-playlist-utility/issues)
![PyPI](https://img.shields.io/pypi/v/spotify-playlist-utility)
[![code with hearth by ryanwarrick](https://img.shields.io/badge/%3C%2F%3E%20with%20%E2%99%A5%20by-ryanwarrick-ff1414.svg?style=flat-square)](https://github.com/ryanwarrick)


# Spotify-Playlist-Utility

Python utility to archive, restore, & shuffle Spotify playlists.

Spotify's service has a few downsides. Fortunately, they offer a fairly nice Web API. To fill in these feature gaps, I developed a Python cmd line utility which offers the following features:
* Export: Spotify Saved (Liked) Tracks -> CSV track listing
* Export: Spotify Playlist -> CSV track listing
* Import: CSV track listing -> Spotify Playlist
* List: Spotify Playlists (name & track count)

## Project Context:

Long ago, I informally self-taught myself Python in a mostly hobby capacity. As my cybersecurity/IT career has progressed, I've worked to formalize my Python skills so that I could write compliant, well-documented, open-source ready, and packaged/deployable Python packages.

I used this project idea as an opportunity to build out a full-fledged Python project repo.
For example, this project...
* has a package with various modules within it
* is easily distributable: .tar.gz/.whl support and on the Python Package Index (PyPI/pip)
* has sphinx auto-generated docs documenting classes/functions
* includes .vscode configs for easy development in VS Code
* config file support
* command line option/argument style application
 
## Installation 

Prerequisite: System must have Python 3.6+ installed (and pip - included with Python). See [Python docs here](https://wiki.python.org/moin/BeginnersGuide/Download) for help installing.

Next, run the following pip command in the terminal to install the package from the Python Package Index:
```
python -m pip install spotify-playlist-utility
```

See gif illustrating pip install of the package:

![Install Demo](docs/images/install_demo.gif)

## Setup/Configuration

This script interacts with Spotify's Web API via the [spotipy](https://github.com/plamere/spotipy) open-source Python library. Therefore, we must register an application with Spotify's developer site and add the necessary data to a configuration file.

### Steps: 
1) To get started using the API, create an app on [Spotify's developer site](https://developer.spotify.com/dashboard/).
    * Log in with your Spotify account credentials.
    * Click "Create an App"
    * Provide an app name/description and click "Create".
    * On the following page, click "Edit Settings".
    * Add "http://localhost:8888/callback" to the "Redirect URIs", click "add" then "save".
    * Take note of the "Client ID" and "Client Secret" on the Application Overview page.
2) Create a customized configuration file for use by the package's 'spotify-playlist-utility' console command:
    * Download a copy of the [template configuration file ('config.ini') ](https://github.com/ryanwarrick/spotify-playlist-utility/blob/master/config.ini) found  at the project root.
        * (Note: If you are working from source, you can grab the same file from your clone of the repo)
    * Edit the file to overwrite the placeholder values with the 'Client ID' and 'Client Secret' we previously noted in Step 1. You can leave 'RedirectURI' unmodified. See example below...

```
[DEFAULT]
ClientID = ABCDEFGHI
ClientSecret = 123456789
RedirectURI = http://localhost:8888/callback
```

## Usage/Examples

For help, execute the following in the console
```
spotify-playlist-utility --help
```
### Export Spotify Playlist Tracks (to .csv file)
```
spotify-playlist-utility <config_ini_file_path> -p <output_csv_file_path>
```
![Export Playlist Tracks Demo](docs/images/export_playlist_tracks_demo.gif)

### Import Tracks to Spotify Playlist (from matching .csv file)
```
spotify-playlist-utility <config_ini_file_path> -i <input_csv_file_path>
```
![Import Tracks to Playlist Demo](docs/images/import_tracks_to_playlist_demo.gif)

### Shuffle Spotify Playlist Tracks
```
spotify-playlist-utility <config_ini_file_path> -z
```
![Shuffle Playlist](docs/images/shuffle_playlist_demo.gif)
  
## Contributors

- Development: [@ryanwarrick - Github](https://www.github.com/ryanwarrick)
- Logo Asset: [@UniTheDino - Twitter](https://twitter.com/unithedino)
import os
from dotenv import load_dotenv
from functions import (
    download_from_playlist,
    set_mp3_metadata_with_cover,
    clean_mp3_filenames,
    get_album_details,
)

# Useful website for artwork: https://www.discogs.com/
load_dotenv()

# Set these variables
ARTIST = ""
ALBUM = [
    "",
]
PLAYLIST_URL = [
    "",
]
# can edit base folder in .env file
BASE_FOLDER = os.getenv("BASE_PATH")
ARTIST_FOLDER_PATH = os.path.join(BASE_FOLDER, ARTIST)

for album, playlist_url in zip(ALBUM, PLAYLIST_URL):

    album_folder_path = os.path.join(ARTIST_FOLDER_PATH, album)
    # # Create folders
    os.makedirs(ARTIST_FOLDER_PATH, exist_ok=True)
    os.makedirs(album_folder_path, exist_ok=True)
    # # Download the songs
    download_from_playlist(album_folder_path, playlist_url)
    # # Fix names
    clean_mp3_filenames(album_folder_path)
    # # # Get Metadata from disco API
    year = get_album_details(ARTIST, album, album_folder_path)
    if year:
        # Add meta data such as artist and year
        set_mp3_metadata_with_cover(album_folder_path, ARTIST, album, year)

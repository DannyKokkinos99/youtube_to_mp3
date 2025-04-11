import yt_dlp as youtube_dl
import eyed3
import os
import re
import subprocess
import discogs_client
import requests
from dotenv import load_dotenv
from functions import (
    download_from_playlist,
    set_mp3_metadata_with_cover,
    clean_mp3_filenames,
)


# Useful website for artwork: https://www.discogs.com/
load_dotenv()

# Set these variables
ARTIST = "Twenty One Pilots"
ALBUM = "Vessel"
YEAR = "2013"
PLAYLIST_URL = (
    "https://www.youtube.com/playlist?list=PLoDAYWBKduzh5L8ISW_etHN0fBdzB_HRg"
)
# can edit base folder in .env file
BASE_FOLDER = os.getenv("BASE_PATH")
ARTIST_FOLDER_PATH = f"{BASE_FOLDER}/{ARTIST}"
ALBUM_FOLDER_PATH = f"{ARTIST_FOLDER_PATH}/{ALBUM}"

# Create folders
os.makedirs(ARTIST_FOLDER_PATH, exist_ok=True)
os.makedirs(ALBUM_FOLDER_PATH, exist_ok=True)
# Download the songs
download_from_playlist(ALBUM_FOLDER_PATH, PLAYLIST_URL)
# Fix names
clean_mp3_filenames(ALBUM_FOLDER_PATH)
# Add meta data such as title, album and artist
set_mp3_metadata_with_cover(ALBUM_FOLDER_PATH, ARTIST, ALBUM, YEAR)
